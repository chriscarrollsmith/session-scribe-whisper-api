import os
import json
import tempfile
from google.cloud import storage
from google.oauth2 import service_account
from api import gcloud
import pytest
from dotenv import load_dotenv

load_dotenv()

def test_gcloud_upload_and_delete():
    # Load the credentials from the environment variable
    service_account_info = json.loads(os.environ["GCLOUD_CREDENTIALS"])
    credentials = service_account.Credentials.from_service_account_info(service_account_info)

    # Define your bucket name
    bucket_name = "session-scribe-bucket" # replace with your bucket name

    # Create a dummy file for testing
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
        tmp.write(b"This is a dummy file.")
        tmp_path = tmp.name

    # Upload the file to Google Cloud Storage
    public_url = gcloud.upload_to_gcloud(tmp_path, credentials, bucket_name)

    # Verify that the file was uploaded correctly by downloading it to a new location
    client = storage.Client(credentials=credentials)
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(os.path.basename(tmp_path))
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as downloaded_tmp:
        blob.download_to_file(downloaded_tmp)
        downloaded_tmp_path = downloaded_tmp.name

    # Check if the content of the downloaded file matches the original
    with open(downloaded_tmp_path, 'r') as file:
        data = file.read()
    assert data == "This is a dummy file."

    # Delete the file from Google Cloud Storage
    blob.delete()

    # Verify that the file was deleted correctly by attempting to download it again
    with pytest.raises(Exception):
        blob.download_to_filename(downloaded_tmp_path)

    # Cleanup the local dummy files
    os.remove(tmp_path)
    os.remove(downloaded_tmp_path)
