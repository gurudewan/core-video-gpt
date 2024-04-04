import os
import glob
from app.helpers.gcs_helper import gcs
from app.consts import consts
import shutil

from langchain.schema import Document
import json
from typing import Iterable

from datetime import timedelta
from app.types.type_models import ViewedImage, ViewedVideo

# GCS FILES helpers


from google.cloud import storage
from PIL import Image
from io import BytesIO


def write_image_to_gcs(image: Image, blob_name: str) -> str:
    """Writes a PIL Image to Google Cloud Storage without saving it locally.

    Args:
        image (PIL.Image): The image to write to GCS.
        bucket_name (str): The name of the bucket to write to.
        blob_name (str): The name of the blob to create in the bucket.

    Returns:
        str: The public URL of the uploaded image.
    """

    bucket_name = consts().BUCKET_NAME

    # Create a BytesIO object and save the image to it
    byte_stream = BytesIO()
    image.save(byte_stream, format="JPEG")

    # Go to the start of the BytesIO object
    byte_stream.seek(0)

    # Get the GCS bucket
    bucket = gcs.client.bucket(bucket_name)

    # Create a new blob in the bucket
    blob = bucket.blob("/tmp/youtube/" + blob_name)

    # Upload the image to the blob from the BytesIO object
    blob.upload_from_file(byte_stream, content_type="image/jpeg")

    # Make the blob publicly accessible and return its public URL
    blob.make_public()
    return blob.public_url


def download_video_from_gcs(video_id: str, destination_file_path: str = None) -> None:
    """Downloads a video from Google Cloud Storage.

    Args:
        video_id (str): The ID of the video.
        destination_file_path (str): The path where the video will be saved.
    """
    # Define the blob name
    blob_name = f"/tmp/youtube/{video_id}/video.mp4"

    destination_file_path = blob_name

    # Download the blob to a file
    gcs.download_blob(blob_name, destination_file_path)

    return


def delete_video_from_gcs(video_id: str) -> None:
    """Deletes a video from Google Cloud Storage.

    Args:
        video_id (str): The ID of the video.
    """
    # Define the blob name
    blob_name = f"/tmp/youtube/{video_id}/video.mp4"

    # Delete the blob
    gcs.delete_blob(blob_name)


def make_video_public(video_id: str) -> None:
    """Makes a blob in Google Cloud Storage publicly accessible.

    Args:
        video_id (str): The ID of the video.
    """
    bucket_name = consts().BUCKET_NAME
    blob_name = f"/tmp/youtube/{video_id}/video.mp4"

    # Get the GCS bucket
    bucket = storage.Client().bucket(bucket_name)

    # Get the blob
    blob = bucket.blob(blob_name)

    # Make the blob publicly accessible
    blob.make_public()


def make_video_private(video_id: str) -> None:
    """Makes a blob in Google Cloud Storage private.

    Args:
        video_id (str): The ID of the video.
    """
    bucket_name = consts().BUCKET_NAME
    blob_name = f"/tmp/youtube/{video_id}/video.mp4"

    # Get the GCS bucket
    bucket = storage.Client().bucket(bucket_name)

    # Get the blob
    blob = bucket.blob(blob_name)

    # Make the blob private
    blob.acl.user("allUsers").revoke_read()
    blob.acl.save()


def get_signed_url(video_id: str) -> str:
    """Generates a signed URL for a video in Google Cloud Storage.

    Args:
        video_id (str): The ID of the video.

    Returns:
        str: The signed URL of the video.
    """
    bucket_name = consts().BUCKET_NAME
    blob_name = f"/tmp/youtube/{video_id}/video.mp4"

    # Get the GCS bucket
    bucket = storage.Client().bucket(bucket_name)

    # Get the blob
    blob = bucket.blob(blob_name)

    # Generate the signed URL
    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=30),  # The URL will be valid for 30 minutes
        method="GET",
    )

    print("the video has a url")
    print(url)

    return url


def get_set_file(file_type, video_id, file_content):
    "file type must be in id | view |"
    if file_type == "id":
        file_name = f"info.json"
    else:
        file_name = file_type

    file_path = f"{video_id}/{file_name}"
    if not gcs.blob_exists(file_path):
        gcs.create_blob(file_path)
        # write the file_content to the blob
    return gcs.get_blob(file_path)


def file_exists(file_path):
    return gcs.blob_exists(file_path)


def video_exists(video_id):
    return gcs.folder_exists(f"/tmp/youtube/{video_id}")


def vector_db_exists(video_id):
    return gcs.folder_exists(f"/tmp/youtube/{video_id}/faiss.index/index.faiss")


def stream_var_into_gcs(data, blob_name):
    if isinstance(data, ViewedImage):
        data = data.model_dump()
    elif isinstance(data, ViewedVideo):
        data = data.model_dump()
    elif isinstance(data, list) and all(isinstance(item, ViewedImage) for item in data):
        data = [item.model_dump() for item in data]
    gcs.stream_json_to_gcs(data, blob_name)


def load_var_from_gcs(blob_name):
    json_str = gcs.stream_blob(blob_name)
    data = json.loads(json_str)
    return data


# LOCAL FILES helpers


def find_tmp_file(video_id, extension):
    files = glob.glob(f"tmp/youtube/{video_id}/*.{extension}")
    return files[0] if files else None


def save_docs_to_json(array: Iterable[Document], file_path: str) -> None:
    data = [doc.json() for doc in array]
    with open(file_path, "w") as json_file:
        json.dump(data, json_file)


def load_docs_from_json(file_path) -> Iterable[Document]:
    with open(file_path, "r") as json_file:
        data = json.load(json_file)
    return [Document(**item) for item in data]


def find_and_format_file(video_id, filename, extension):
    file_path = find_tmp_file(video_id, extension)
    if file_path:
        formatted_file_path = f"tmp/youtube/{video_id}/{filename}.{extension}"
        os.rename(file_path, formatted_file_path)
        return formatted_file_path
    else:
        print("! a file path could not be found")
        return None


def delete_folder(folder_path):
    # Check if the folder exists
    if os.path.exists(folder_path):
        # If the folder exists, delete it
        shutil.rmtree(folder_path)
    return
