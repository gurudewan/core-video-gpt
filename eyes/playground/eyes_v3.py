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
import time

from memory_profiler import memory_usage


model, preprocess = clip.load("./torch_cache/ViT-B-32.pt")


# import helpers.tensor_helper as tensor_helper
import filer

from consts import consts

# Define the frame rate
FRAME_RATE = 1  # this is not used anymore
FRAME_SKIP = 24 * 1  # 24 * X means every Xth second (due to ~ 24fps)
# I THINK 24 *2, i.e. every 2seconds is the right amount?

COS_SIMILARITY_THRESHOLD_FOR_NEIGHBOUR_FRAMES = 0.5
COS_SIMILARITY_THRESHOLD_FOR_GROUPS = 0.7

PIXEL_DIFFERENCE_THRESHOLD_FOR_NEIGHBOUR_FRAMES = 0.25


class Frame:
    frame: int
    time: int
    group: int = -1


class Group:
    id: int
    sections: List[Tuple[float, float]] = []


def see(video_id, info):

    local_video_path = f"eyes/playground/videos/{video_id}"

    # local_video_path = f"tmp/youtube/{video_id}/video.mp4"
    base_view_url = f"/tmp/youtube/{video_id}/view/"

    first_pass_groups = collapse_neighbours(local_video_path)

    return


def collapse_neighbours(video_url):

    print("=== collapsing neighbours ===")

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

    # Initialize the frame & group count
    frame_count = 0
    group_count = 0

    # Initialize the results list
    results = []

    # Initialize the previous frame & group
    prev_frame = None
    prev_group = None

    group_id = 0

    while True:
        # Read the next frame from the video
        ret, frame = video.read()

        # If the frame was not successfully read then break the loop
        if not ret:
            break

        # If this is the first frame or a frame we want to process

        if prev_frame is None or frame_count % FRAME_SKIP == 0:

            # if not blurry
            # if not motion detected ...
            # use sci-kit SSIM ?s

            # Get the timestamp of the current frame
            timestamp = frame_count / fps

            if prev_frame is not None:
                pixel_diff = calculate_pixel_difference(prev_frame, frame)

                # print(f"{pixel_diff} at timestamp {timestamp:.2f}")
                if pixel_diff < 25:

                    # collapse the frames into the same group
                    # pprint("similar by pixels")
                    group_id = prev_group

                elif 25 <= pixel_diff < 80:
                    # pprint(f"DOING EMBED at {timestamp:.0f}")
                    # use embeddings to decide whether similar or not
                    similarity = calculate_embeddings_similarity(prev_frame, frame)

                    # store the embeddings when they are calculated

                    if similarity >= COS_SIMILARITY_THRESHOLD_FOR_NEIGHBOUR_FRAMES:
                        # pprint("similar by embeddings")
                        group_id = prev_group
                    else:
                        minutes, seconds = divmod(timestamp, 60)
                        pprint(f"new group @ {minutes:.0f}m {seconds:.0f}s")

                        # pprint("difference by embeddings")
                        # pprint(f"EMBED difference at {timestamp:.0f}")
                        group_count += 1
                        group_id = group_count
                        results.append((frame, timestamp, group_id))

                elif pixel_diff >= 80:
                    minutes, seconds = divmod(timestamp, 60)
                    pprint(f"new group @ {minutes:.0f}m {seconds:.0f}s")
                    # pprint(f"PIXEL difference {pixel_diff:.0f}% at {timestamp:.0f}")
                    # pprint("difference by pixels")
                    group_count += 1
                    group_id = group_count
                    results.append((frame, timestamp, group_id))

        prev_group = group_id

        # Update the previous frame
        prev_frame = frame

        # Increment the frame count
        frame_count += 1

    # Release the video file
    video.release()

    pprint("THE RESULTS")

    pprint(f"{group_count}")

    for i in results:
        minutes, seconds = divmod(i[1], 60)
        pprint(f"group id: {i[2]} at timestamp {minutes:.0f}m {seconds:.0f}s")

    return results


# _______________________________ PIXEL DIFF _______________________________


def calculate_pixel_difference(img1: np.array, img2: np.array) -> float:
    diff = cv2.absdiff(img1, img2)

    if len(diff.shape) == 3:
        diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    thresh_diff = cv2.threshold(diff, 15, 255, cv2.THRESH_BINARY)[1]

    thresh_diff = cv2.threshold(diff, 15, 255, cv2.THRESH_BINARY)[1]

    # Calculate the difference between the 2 images
    total_pixels = img1.shape[0] * img1.shape[1] * 1.0
    diff_on_pixels = cv2.countNonZero(thresh_diff) * 1.0
    difference_measure = (diff_on_pixels / total_pixels) * 100  # converted to %
    # print("difference_measure: {}".format(difference_measure))
    return difference_measure


# _______________________________ EMBEDDINGS _______________________________


def calculate_embeddings_similarity(prev_frame, curr_frame):
    prev_embeddings = get_frame_embeddings(prev_frame)
    # TODO cache this
    curr_embeddings = get_frame_embeddings(curr_frame)

    similarity = torch.cosine_similarity(prev_embeddings, curr_embeddings).item()

    return similarity


def get_frame_embeddings(frame):
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


# _______________________________ RULES BASED SAMPLING _______________________________


def random_sample_middle_frames(video_capture: cv2.VideoCapture) -> list:
    """
    Takes a random sample of the middle bits of the video.
    To see if this is a single shot video.
    """
    frame_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    start_frame = int(frame_count * 0.05)
    end_frame = int(frame_count * 0.95)

    # Calculate the number of frames to sample after skipping frames
    sample_count = int((end_frame - start_frame) / FRAME_SKIP)

    # Use np.arange to create a range of frames to sample, skipping frames according to FRAME_SKIP
    frames_to_sample = np.arange(start_frame, end_frame, FRAME_SKIP, dtype=int)

    print(
        f"Total frames: {frame_count}, Sampling range: {start_frame}-{end_frame}, Number of frames to sample: {sample_count}"
    )

    sampled_frames = []
    for frame_number in frames_to_sample:
        video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = video_capture.read()
        if ret:
            sampled_frames.append(frame)
    return sampled_frames


if __name__ == "__main__":

    print("===eyes are in playground mode===")

    # video_id = input("Please enter the video ID: ")

    # video_id = "elon_sama_480p.mp4"
    video_id = "lex_sam_480p.mp4"

    # info = filer.load_var_from_gcs(f"tmp/youtube/{video_id}/info.json")
    info = None

    start = time.time()
    see(video_id, info)
    end = time.time()

    elapsed_time = end - start
    print(f"Elapsed time: {elapsed_time} seconds")
