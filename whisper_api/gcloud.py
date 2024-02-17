from google.cloud import storage
import os

def upload_to_gcloud(path: str, credentials, bucket_name: str = os.environ[os.environ["BUCKET_NAME])) -> str:
    """
    Uploads a file to a specified Google Cloud Storage bucket.

    Args:
        path (str): The path to the file that needs to be uploaded.
        credentials: The credentials object required to authenticate with Google Cloud.
        bucket_name (str, optional): The name of the bucket to which the file will be uploaded. Defaults to 'session-scribe-bucket'.

    Returns:
        str: The public URL of the uploaded file in Google Cloud Storage.

    Example:
        pdf_url = upload_to_gcloud('path/to/file.pdf', credentials)
    """
    # Create a client for interacting with Google Cloud Storage
    storage_client = storage.Client(credentials=credentials)

    # Get the specified bucket (or the default one if not provided)
    bucket = storage_client.get_bucket(bucket_or_name=bucket_name)

    # Create a blob object representing the file to be uploaded
    blob = bucket.blob(os.path.basename(p=path))

    # Upload the file from the given path
    blob.upload_from_filename(filename=path)

    # Return the public URL of the uploaded file
    return blob.public_url
