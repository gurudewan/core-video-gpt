from google.cloud import storage
import json
import os

import consts
from helpers.json_encoder import DocumentEncoder


class GCSHelper:
    def __init__(self):
        self.bucket_name = consts.BUCKET_NAME
        self.client = storage.Client()
        self.bucket = self.client.get_bucket(self.bucket_name)

    def stream_json_to_gcs(self, data, blob_name):
        blob = self.bucket.blob(blob_name)
        # Use custom DocumentEncoder to also handle langchain Documents
        data_json = json.dumps(data, cls=DocumentEncoder)
        blob.upload_from_string(data_json)

    def upload_blob(self, source_file_name, destination_blob_name):
        """Uploads a file to the bucket."""
        blob = self.bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)

    def download_blob(self, source_blob_name, destination_file_name):
        """Downloads a blob from the bucket."""
        blob = self.bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_name)

    def stream_blob(self, blob_name):
        """Streams a blob from the bucket."""
        blob = self.bucket.blob(blob_name)
        return blob.download_as_text()

    def blob_exists(self, blob_name):
        """Checks if a blob exists in the bucket."""
        blob = self.bucket.blob(blob_name)
        return blob.exists()

    def read_json(self, source_file_name):
        """Reads a JSON file from the bucket into memory."""
        blob = self.bucket.blob(source_file_name)
        json_data = blob.download_as_text()
        data = json.loads(json_data)
        return data

    def write_json(self, data, destination_blob_name):
        """Writes a JSON object to the bucket."""
        blob = self.bucket.blob(destination_blob_name)
        json_data = json.dumps(data)
        blob.upload_from_string(json_data, content_type="application/json")
        return

    def folder_exists(self, folder_name):
        """Checks if a folder exists in the bucket."""
        blobs = self.client.list_blobs(self.bucket_name, prefix=folder_name)
        for blob in blobs:
            return True
        return False

    def upload_folder_to_gcs(self, local_directory_path, gcs_directory_path):
        for root, dirs, files in os.walk(local_directory_path):
            for local_file in files:
                local_file_path = os.path.join(root, local_file)
                relative_path = os.path.relpath(local_file_path, local_directory_path)
                gcs_file_path = os.path.join(gcs_directory_path, relative_path)
                self.upload_blob(local_file_path, gcs_file_path)

    def download_folder_from_gcs(self, gcs_folder_path, local_folder_path):
        """Downloads a folder and all its subfolders and files from the bucket."""
        blobs = self.client.list_blobs(self.bucket_name, prefix=gcs_folder_path)
        for blob in blobs:
            if not os.path.exists(os.path.dirname(blob.name)):
                os.makedirs(os.path.dirname(blob.name))
            blob.download_to_filename(blob.name)

    def delete_folder(self, folder_path):
        """Deletes a folder and all its contents from the bucket."""
        blobs = self.client.list_blobs(self.bucket_name, prefix=folder_path)
        for blob in blobs:
            blob.delete()

    def delete_blob(self, blob_name):
        """Deletes a blob from the bucket."""
        blob = self.bucket.blob(blob_name)
        blob.delete()

    def check_if_seen(self, video_id):
        key_frames_path = f"/tmp/{video_id}/key_frames/"
        view_path = f"/tmp/{video_id}/view/"

        return self.blob_exists(key_frames_path) and self.blob_exists(view_path)


gcs = GCSHelper()

if __name__ == "__main__":
    video_id = "uKrnx81zdnQX"
    print(gcs.folder_exists(f"/tmp/youtube/{video_id}/"))
