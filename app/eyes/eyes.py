import cv2
import numpy as np
import torch
import clip
from typing import List, Tuple
from torch.nn import CosineSimilarity
from PIL import Image
import os
from sklearn.cluster import KMeans
from pprint import pprint
import asyncio

from . import llava_api
from . import gptvision
import app.file_api.filer as filer

model, preprocess = clip.load("./torch_cache/ViT-B-32.pt")

# TODO optimise these constants

# Define the frame rate
FRAME_RATE = 1  # this is not used anymore
FRAME_SKIP = 24 * 60  # 24 * X means everyth Xth second (due to ~ 24fps)

FOCUS_THRESHOLD = 500  # Adjust this value based on your needs
MOTION_THRESHOLD = 10000  # Adjust this value based on your needs

COS_SIMILARITY_THRESHOLD_FOR_NEIGHBOUR_FRAMES = 0.8
COS_SIMILARITY_THRESHOLD_FOR_GROUPS = 0.7


async def see(video_id, info):
    local_video_path = f"tmp/youtube/{video_id}/video.mp4"
    base_view_url = f"/tmp/youtube/{video_id}/view/"

    os.makedirs(f"tmp/youtube/{video_id}/", exist_ok=True)

    # local_video_path = f"eyes/test_videos/{video_id}.mp4"
    # ! bug where video is not downloaded to /tmp?

    all_frame_embeddings = extract_all_frames(local_video_path)

    # Save all_frame_embeddings to a file
    """    with open(f"{video_id}/all_frame_embeddings.pkl", "wb") as f:
        pickle.dump(all_frame_embeddings, f)

    with open(f"{video_id}/all_frame_embeddings.pkl", "wb") as f:
        all_frame_embeddings = pickle.load(f)"""

    # print(all_frame_embeddings)
    key_scenes = extract_key_scenes(all_frame_embeddings)
    # print(key_scenes)

    grouped_frames, frame_groups = group_similar_frames(key_scenes)

    # Print grouped frames without embeddings
    """
    for _, start_timestamp, end_timestamp, group_id in grouped_frames:
        print(
            f"Start Timestamp: {start_timestamp}, End Timestamp: {end_timestamp}, Group: {group_id}"
        )
    """
    # Print frame_groups without embeddings
    """
    for _, periods, group_id in frame_groups:
        print(f"Periods: {periods}, Group: {group_id}")
    """
    # write grouped_frames, frame_groups to gcs
    grouped_frames = [(start, end, group) for _, start, end, group in grouped_frames]
    frame_groups = [(periods, group_id) for _, periods, group_id in frame_groups]

    filer.stream_var_into_gcs(grouped_frames, base_view_url + "grouped_frames.json")
    filer.stream_var_into_gcs(frame_groups, base_view_url + "frame_groups.json")

    # write the thumbnails from frame_groups to gcs
    image_urls_with_metadata = write_key_scenes_to_memory(
        frame_groups, local_video_path, video_id
    )
    # send the thumbnails to image 2 text
    # view = await llava_api.async_batch_caption_images(image_urls_with_metadata)
    view = await gptvision.async_batch_caption_images(image_urls_with_metadata, info)

    filer.stream_var_into_gcs(view, base_view_url + "view.json")

    # pprint(view)

    print(f"===== summary of view =====")
    # log the summary of the view
    num_frames = len(view)  # Assuming view is a list of frames
    # first_frame = view[0] if num_frames > 0 else None
    # last_frame = view[-1] if num_frames > 0 else None

    print(f"##### num of frames captioned: {num_frames}")

    print("===== viewing complete =====")

    return view


def extract_all_frames(video_url):
    # Open the video file
    video = cv2.VideoCapture(video_url)

    # Check if video opened successfully
    if not video.isOpened():
        print("Error opening video file")
        return None

    # Get the frames per second of the video
    fps = video.get(cv2.CAP_PROP_FPS)

    # Calculate the frame skip value
    frame_skip = FRAME_SKIP  # int(fps * FRAME_RATE)

    # Initialize the frame count
    frame_count = 0

    # Initialize the results list
    results = []

    # Initialize the previous frame
    prev_frame = None

    while True:
        # Read the next frame from the video
        ret, frame = video.read()

        # If the frame was not successfully read then break the loop
        if not ret:
            break

        # If this is a frame we want to process
        if frame_count % FRAME_SKIP == 0:
            # Get the timestamp of the current frame
            timestamp = frame_count / fps

            # Calculate the variance of the Laplacian (focus measure)
            # focus_measure = variance_of_laplacian(frame)

            # Calculate the motion measure with the previous frame
            # motion_measure = calculate_motion(prev_frame, frame)

            # TODO calculate the pixel subtraction

            embeddings = get_image_embeddings(frame)

            # Store the embeddings and timestamp in the results list
            results.append((embeddings, timestamp))
            # print("on timestamp " + str(round(timestamp, 2)))
            """
            # Only calculate embeddings if the focus measure is above the threshold and motion measure is below the threshold
            if (
                focus_measure > FOCUS_THRESHOLD
            ):  # and motion_measure < MOTION_THRESHOLD:
                # Get the embeddings of the image
                embeddings = get_image_embeddings(frame)

                # Store the embeddings and timestamp in the results list
                results.append((embeddings, timestamp))
                print("on timestamp " + str(round(timestamp, 2)))
            else:
                print("discarded a blurry or high motion frame")

            """

        # Update the previous frame
        prev_frame = frame

        # Increment the frame count
        frame_count += 1

    # Release the video file
    video.release()

    return results


def calculate_motion(prev_frame, curr_frame):
    if prev_frame is None:
        return 0
    # Calculate the absolute difference between the current frame and the previous frame
    frame_diff = cv2.absdiff(prev_frame, curr_frame)
    # Sum up the differences to get a measure of motion
    motion_measure = np.sum(frame_diff)

    return motion_measure


def variance_of_laplacian(image):
    # compute the Laplacian of the image and then return the focus
    # measure -- the variance of the Laplacian
    return cv2.Laplacian(image, cv2.CV_64F).var()


def get_image_embeddings(frame):
    # Convert the image from BGR to RGB
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Convert the image to a PIL Image
    image = Image.fromarray(frame)

    # Preprocess the image
    image_input = preprocess(image).unsqueeze(0)

    # Calculate the embeddings
    with torch.no_grad():
        embeddings = model.encode_image(image_input)

    return embeddings


def extract_key_scenes(
    results: List[Tuple[torch.Tensor, float]],
    threshold: float = COS_SIMILARITY_THRESHOLD_FOR_NEIGHBOUR_FRAMES,
) -> List[Tuple[torch.Tensor, float, float]]:
    # Initialize the cosine similarity function
    cos_sim = CosineSimilarity(dim=0)

    # Initialize the key scenes list with the first scene
    key_scenes = [(results[0][0], round(results[0][1], 3), round(results[0][1], 3))]

    # Iterate over the scenes
    for i in range(1, len(results)):
        # Calculate the cosine similarity between the current scene and the last key scene
        similarity = cos_sim(key_scenes[-1][0], results[i][0]).mean().item()

        # If the similarity is less than the threshold, add the current scene to the key scenes
        if similarity < threshold:
            # Update the end timestamp of the last key scene
            key_scenes[-1] = (
                key_scenes[-1][0],
                key_scenes[-1][1],
                round(results[i - 1][1], 3),
            )

            # Add the current scene to the key scenes
            key_scenes.append(
                (results[i][0], round(results[i][1], 3), round(results[i][1], 3))
            )

    # Update the end timestamp of the last key scene
    key_scenes[-1] = (key_scenes[-1][0], key_scenes[-1][1], round(results[-1][1], 3))

    return key_scenes


from sklearn.cluster import KMeans


def group_similar_frames(
    key_frames: List[Tuple[torch.Tensor, float, float]],
    threshold: float = 0.5,
) -> List[Tuple[torch.Tensor, float, float, int]]:
    # Initialize the cosine similarity function
    cos_sim = CosineSimilarity(dim=0)

    # Initialize the grouped frames list with the first frame
    grouped_frames = [
        (key_frames[0][0], round(key_frames[0][1], 3), round(key_frames[0][2], 3), 0)
    ]

    # Initialize the list that stores one frame per group
    frame_groups = [
        (
            key_frames[0][0],
            [(round(key_frames[0][1], 3), round(key_frames[0][2], 3))],
            0,
        )
    ]

    # Initialize the group count
    group_count = 0

    # Iterate over the frames
    for i in range(1, len(key_frames)):
        # Initialize a flag to indicate if the current frame is similar to any previous frame
        is_similar = False

        # Iterate over the grouped frames
        for j in range(len(grouped_frames)):
            # Calculate the cosine similarity between the current frame and the j-th frame in the group
            similarity = cos_sim(grouped_frames[j][0], key_frames[i][0]).mean().item()

            # If the similarity is greater than or equal to the threshold
            if similarity >= threshold:
                # Set the flag to True and update the group of the current frame to the group of the j-th frame
                is_similar = True
                group_id = grouped_frames[j][3]
                # Add the current frame to the existing group in frame_groups
                frame_groups[group_id][1].append(
                    (round(key_frames[i][1], 3), round(key_frames[i][2], 3))
                )
                break

        # If the current frame is not similar to any previous frame, increment the group count
        if not is_similar:
            group_count += 1
            group_id = group_count

            # Add the current frame to the one_frame_per_group list
            frame_groups.append(
                (
                    key_frames[i][0],
                    [(round(key_frames[i][1], 3), round(key_frames[i][2], 3))],
                    group_id,
                )
            )

        # Add the current frame to the grouped frames with its group
        grouped_frames.append(
            (
                key_frames[i][0],
                round(key_frames[i][1], 3),
                round(key_frames[i][2], 3),
                group_id,
            )
        )

    """     
    #! k means clustering > made it worse
    # For each group, find the centroid frame
    for group in frame_groups:
        embeddings_list, _, _ = group
        if isinstance(embeddings_list, list):
            embeddings = torch.stack(
                embeddings_list
            )  # Ensure embeddings_list is a list of tensors
            kmeans = KMeans(n_clusters=1, random_state=0).fit(embeddings)
            centroid = kmeans.cluster_centers_[0]
            centroid_frame = embeddings[
                torch.argmin(torch.norm(embeddings - centroid, dim=1))
            ]

            # Replace the group's representative frame with the centroid frame
            group[0] = centroid_frame
        else:
            print("embeddings_list is not a list") """

    return grouped_frames, frame_groups


def write_key_scenes_to_memory(frame_groups, video_url, video_id):
    # Open the video file
    video = cv2.VideoCapture(video_url)

    image_urls_with_metadata = []

    # Check if video opened successfully
    if not video.isOpened():
        print("Error opening video file")
        return

    for periods, group_id in frame_groups:
        median_index = len(periods) // 2

        # Set the video position to the desired timestamp in milliseconds
        video.set(cv2.CAP_PROP_POS_MSEC, periods[median_index][0] * 1000)

        # Read the frame at the current video position
        ret, frame = video.read()

        # If the frame was not successfully read then continue to the next timestamp
        if not ret:
            continue

        # Resize the frame to a medium resolution
        frame = cv2.resize(frame, (640, 480))

        # Convert the frame to a PIL Image
        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # Write the image to GCS and get the public URL
        image_url = filer.write_image_to_gcs(
            image, f"{video_id}/key_frames/{group_id}.jpg"
        )

        image_urls_with_metadata.append(
            {"image_url": image_url, "group_id": group_id, "periods": periods}
        )

        # print("----")
        # print(image_url)

    # Release the video file
    video.release()

    return image_urls_with_metadata


if __name__ == "__main__":
    import time

    print("===testing mode===")

    video_id = input("Please enter the video ID: ")

    info = filer.load_var_from_gcs(f"tmp/youtube/{video_id}/info.json")

    start = time.time()
    asyncio.run(see(video_id, info))
    end = time.time()

    elapsed_time = end - start
    print(f"Elapsed time: {elapsed_time} seconds")
