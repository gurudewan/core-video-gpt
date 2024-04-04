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
import app.file_api.filer as filer

from app.consts import consts

# Define the frame rate
FRAME_RATE = 1  # this is not used anymore
FRAME_SKIP = 24 * 1  # 24 * X means every Xth second (due to ~ 24fps)
# I THINK 24 *2, i.e. every 2seconds is the right amount?


def load_video(video_name: str) -> cv2.VideoCapture:
    video_path = f"eyes/playground/videos/{video_name}"
    print(f"Loading video from path: {video_path}")
    return cv2.VideoCapture(video_path)


def get_video_files(directory: str) -> List[str]:
    return [f for f in os.listdir(directory) if f.endswith((".mp4", ".avi", ".mov"))]


def choose_video(videos: List[str]) -> str:
    for index, video in enumerate(videos):
        print(f"{index}: {video}")
    choice = int(input("Enter the number for the video: "))
    chosen_video = videos[choice]
    print(f"User chose video: {chosen_video}")
    return chosen_video


def sample_frames_iterative(video_capture: cv2.VideoCapture):
    frame_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    start_frame = int(frame_count * 0.05)
    end_frame = int(frame_count * 0.95)
    for frame_number in range(start_frame, end_frame, FRAME_SKIP):
        video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = video_capture.read()
        if ret:
            yield frame


def sample_frames(video_capture: cv2.VideoCapture) -> list:
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


def print_frames(frames: list, video_name: str):
    stripped_video_name = video_name.split(".")[0]
    output_dir = f"eyes/playground/videos/{stripped_video_name}/outputs"
    os.makedirs(output_dir, exist_ok=True)
    print(f"Saving frames to directory: {output_dir}")

    for i, frame in enumerate(frames):
        frame_path = os.path.join(output_dir, f"frame_{i}.jpg")
        cv2.imwrite(frame_path, frame)
        print(f"Saved frame {i} to {frame_path}")


# ==================== JPEG MEM COMPARISON ====================


def calculate_all_jpeg_mem_difference(frames: List[np.array]) -> List[Tuple[int, int]]:
    file_sizes = []
    for i, frame in enumerate(frames):
        # Convert the frame to JPEG in memory
        ret, jpeg_frame = cv2.imencode(".jpg", frame)
        if ret:
            # Calculate the memory size of the JPEG frame
            file_size = len(jpeg_frame.tobytes())
            file_sizes.append((i, file_size))

    # Find notable changes in file size
    notable_changes = []
    for i in range(1, len(file_sizes)):
        # If the file size change is notable (e.g., more than 5% change)
        if abs(file_sizes[i][1] - file_sizes[i - 1][1]) / file_sizes[i - 1][1] > 0.05:
            notable_changes.append(file_sizes[i][0])

    return notable_changes


# ==================== PIXELS COMPARISON ====================


def calculate_all_pixel_differences(frames: List[np.array]) -> List[float]:
    differences = []
    for i in range(len(frames) - 1):
        diff = calculate_pixel_difference(frames[i], frames[i + 1])
        if diff > 20:  # 20%
            differences.append(diff)
    return differences


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


# ==================== EMBEDDINGS COMPARISON ====================


def calculate_all_embeddings_similarities(frames: List[np.array]) -> List[float]:
    similarities = []
    for i in range(len(frames) - 1):
        similarity = calculate_embeddings_similarity(frames[i], frames[i + 1])
        similarities.append(similarity)
    return similarities


def calculate_embeddings_similarity(prev_frame, curr_frame):
    prev_embeddings = get_frame_embeddings(prev_frame)
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


# ==================== MAIN ====================


if __name__ == "__main__":
    video_directory = "eyes/playground/videos"
    video_files = get_video_files(video_directory)

    if not video_files:
        print("No video files found in the directory.")
    else:
        print("Available videos:")
        video_name = choose_video(video_files)
        video_capture = load_video(video_name)

    if not video_capture.isOpened():
        print(f"Failed to load video: {video_name}")
    else:

        print("+++++ STAGE 1 : DOING BATCH COMPARISON ++++++")
        start_time_sample_frames_batch = time.time()
        frames = sample_frames(video_capture)
        end_time_sample_frames_batch = time.time()

        print(
            f"Sampling the frames took {end_time_sample_frames_batch - start_time_sample_frames_batch:.2f} seconds"
        )

        mem_usage_batch = memory_usage(
            (sample_frames, (video_capture,)), interval=0.1, timeout=200
        )

        print(f"Memory used: {max(mem_usage_batch) - min(mem_usage_batch):.2f} MiB")

        # print_frames(frames, video_name)

        # Time pixel difference calculation
        start_time_pixel_diff = time.time()
        differences = calculate_all_pixel_differences(frames)
        end_time_pixel_diff = time.time()
        print(
            f"Pixel difference calculation took: {end_time_pixel_diff - start_time_pixel_diff:.2f} seconds"
        )

        # Time embeddings similarity calculation
        start_time_embeddings_sim = time.time()
        similarities = calculate_all_embeddings_similarities(frames)
        end_time_embeddings_sim = time.time()
        print(
            f"Embeddings similarity calculation took: {end_time_embeddings_sim - start_time_embeddings_sim:.2f} seconds"
        )

        print("+++++ STAGE 2 : DOING ONE BY ONE COMPARISON ++++++")
        # Pixel difference iterative calculation
        start_time_pixel_diff_iter = time.time()
        video_capture = load_video(video_name)  # Reload the video
        prev_frame = None
        pixel_differences_iter = []
        for frame in sample_frames_iterative(video_capture):
            if prev_frame is not None:
                pixel_diff = calculate_pixel_difference(prev_frame, frame)
                pixel_differences_iter.append(pixel_diff)
            prev_frame = frame
        end_time_pixel_diff_iter = time.time()
        print(
            f"Iterative pixel difference calculation took: {end_time_pixel_diff_iter - start_time_pixel_diff_iter:.2f} seconds"
        )

        # Embeddings similarity iterative calculation
        start_time_embeddings_sim_iter = time.time()
        video_capture = load_video(video_name)  # Reload the video
        mem_usage_iter = memory_usage(
            (list, (sample_frames_iterative(video_capture),)), interval=0.1, timeout=200
        )

        print(f"Memory used: {max(mem_usage_iter) - min(mem_usage_iter):.2f} MiB")

        prev_frame = None
        embeddings_similarities_iter = []
        for frame in sample_frames_iterative(video_capture):
            if prev_frame is not None:
                similarity = calculate_embeddings_similarity(prev_frame, frame)
                embeddings_similarities_iter.append(similarity)
            prev_frame = frame
        end_time_embeddings_sim_iter = time.time()

        print(
            f"Iterative embeddings similarity calculation took: {end_time_embeddings_sim_iter - start_time_embeddings_sim_iter:.2f} seconds"
        )
        video_capture.release()

        print(f"Processed frames iteratively from the video {video_name}.")
        print(
            f"Total time taken for iterative calculations: {time.time() - start_time_pixel_diff_iter:.2f} seconds"
        )

        print("+++++ STAGE 3 : DOING BATCH COMPARISON ON JPEG ++++++")

        start_time_jpeg_mem_diff = time.time()
        notable_changes = calculate_all_jpeg_mem_difference(frames)
        end_time_jpeg_mem_diff = time.time()
        print(
            f"JPEG memory difference calculation took: {end_time_jpeg_mem_diff - start_time_jpeg_mem_diff:.2f} seconds"
        )

        # Print notable changes in file size
        if notable_changes:
            print("Notable changes in JPEG file size at frames:", notable_changes)
        else:
            print("No notable changes in JPEG file size detected.")
