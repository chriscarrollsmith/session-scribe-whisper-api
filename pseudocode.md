# api.py Pseudocode

1. Import necessary libraries and modules.
2. Initialize logger and FastAPI application.
3. Define the `transcribe_and_return_job_id` function which:
   - Takes parameters: `src_url`, `unique_id`, `session_title`, `presenters`, `is_video`, `password`.
   - Tries to transcribe the audio using the `process_audio.spawn` function.
   - Returns the job id if successful.
   - Logs and raises an HTTPException if an error occurs.
4. Define the `TranscriptionRequest` class which models the request body for the transcription API.
5. Define the `transcribe_and_return_job_id2` function which:
   - Takes a `TranscriptionRequest` object as parameter.
   - Tries to transcribe the audio using the `process_audio.spawn` function.
   - Returns the job id if successful.
   - Logs and raises an HTTPException if an error occurs.

# gcloud.py Pseudocode

1. Import necessary libraries and modules.
2. Define a function `upload_to_gcloud(pdf_path, credentials, bucket_name='session-scribe-bucket')` that:
   - Initializes a Google Cloud Storage client with the provided credentials.
   - Retrieves the specified bucket from the storage client.
   - Creates a blob (object) in the bucket with the same name as the file to be uploaded.
   - Uploads the file to the created blob.
   - Returns the public URL of the uploaded blob.
