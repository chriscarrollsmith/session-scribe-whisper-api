from google.cloud import storage
import os

def upload_to_gcloud(pdf_path, credentials, bucket_name='session-scribe-bucket'):
    """Uploads a file to the bucket."""
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(os.path.basename(pdf_path))

    blob.upload_from_filename(pdf_path)

    return blob.public_url
