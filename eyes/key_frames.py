import cv2

# Define the frame rate
FRAME_RATE = 0.1

from eyes.clipper import get_image_embeddings


def extract_frames(video_path):
    # Open the video file
    video = cv2.VideoCapture(video_path)

    # Check if video opened successfully
    if not video.isOpened():
        print("Error opening video file")
        return

    # Get the frames per second of the video
    fps = video.get(cv2.CAP_PROP_FPS)

    # Calculate the frame skip value
    frame_skip = int(fps * FRAME_RATE)

    # Initialize the frame count
    frame_count = 0

    # Initialize the results list
    results = []

    while True:
        # Read the next frame from the video
        ret, frame = video.read()

        # If the frame was not successfully read then break the loop
        if not ret:
            break

        # If this is a frame we want to process
        if frame_count % frame_skip == 0:
            # Get the timestamp of the current frame
            timestamp = frame_count / fps

            # Get the embeddings of the image
            embeddings = get_image_embeddings(frame)

            # Store the embeddings and timestamp in the results list
            results.append((embeddings, timestamp))

        # Increment the frame count
        frame_count += 1

    # Release the video file
    video.release()

    print("THE RESULTS ARE")
    print(results)

    return results
