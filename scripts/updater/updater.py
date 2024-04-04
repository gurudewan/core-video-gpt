from google.cloud import storage

import sys

from app.consts import consts


import app.file_api.filer as filer

APP_ENV = consts().APP_ENV

BUCKET_NAME = consts().BUCKET_NAME

"""
    Use this file to update things inside the bucket

"""


def get_video_ids() -> list:
    """Gets a list of unique video IDs in a Google Cloud Storage bucket.

    Args:
        bucket_name (str): The name of the bucket.

    Returns:
        list: A list of unique video IDs.
    """
    # Get the GCS bucket
    bucket = storage.Client().bucket(BUCKET_NAME)

    # Create a set to store the unique video IDs
    video_ids = set()

    # Iterate over all the blobs in the bucket
    for blob in bucket.list_blobs(prefix="/tmp/youtube/"):
        # Extract the video_id from the blob name
        parts = blob.name.split("/")

        # Check if the blob name splits into exactly 4 parts
        if len(parts) > 4:
            video_id = parts[3]
            # print(video_id)

            # Add the video_id to the set
            video_ids.add(video_id)

    # Convert the set to a list and return it
    return list(video_ids)


if __name__ == "__main__":
    print(f"making changes in: {BUCKET_NAME}")
    if APP_ENV == "PROD" or BUCKET_NAME == consts().PROD_BUCKET_NAME:
        print("==== beginning updater ====")
        print("")
        print("You are working in PROD. Are you sure?")
        input = input("CONFIRM:")

        if input != "CONFIRM":
            sys.exit()

    video_ids = get_video_ids()

    print(f"{len(video_ids)} videos in GCS")

    for video_id in video_ids:
        # ======= do update function here ========

        print("DOING UPDATE")

        # filer.delete_video_from_gcs(video_id)

# python3 -m app.updater.updater


def fix_view_bug():
    video_folder = f"/tmp/youtube/{video_id}"

    view_path = f"{video_folder}/view/view.json"

    info_path = f"{video_folder}/info.json"

    """         if not filer.file_exists(view_path) or not filer.file_exists(info_path):
        print(f"delete: {video_id}") """

    view = filer.load_var_from_gcs(view_path)
    info = filer.load_var_from_gcs(info_path)

    if info["view"] is None:
        print("found a null view")
        info["view"] = view
        # print(info)
        filer.stream_var_into_gcs(info, info_path)
