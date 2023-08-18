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

# audio.py

1. Import necessary libraries and modules.
2. Define a logger for logging purposes.
3. Define a `Segment` TypedDict with "text", "start", and "end" fields.
4. Define a `AudioMetadata` dataclass with "title_slug" and "audio_url" fields.
5. Define a `DownloadResult` NamedTuple with "data" and "content_type" fields.
6. Define a function `download_audio_file(url: str)` that downloads an audio file from a given URL and returns a `DownloadResult`.
7. Define a function `sizeof_fmt(num, suffix="B")` that formats a size in bytes into a human-readable string.
8. Define a function `store_original_audio(url: str, destination: pathlib.Path, overwrite: bool = False)` that downloads an audio file from a given URL and stores it at a specified destination.
9. Define a function `coalesce_short_transcript_segments(segments: list[Segment])` that combines short transcript segments into longer ones.
10. Define a helper function `_merge_segments(left: Segment, right: Segment)` that merges two segments into one.
11. Define a function `split_silences(path: str, min_segment_length: float = 30.0, min_silence_length: float = 1.0)` that splits an audio file into contiguous chunks using the ffmpeg `silencedetect` filter.

# config.py

1. Import necessary libraries and modules.
2. Define a `ModelSpec` dataclass with "name", "params", and "relative_speed" fields.        
3. Define a function `get_logger(name, level=logging.INFO)` that sets up and returns a logger with a specified name and logging level.
4. Define several constants for directory paths, such as `CACHE_DIR`, `RAW_AUDIO_DIR`, `AUDIO_METADATA_DIR`, `TRANSCRIPTIONS_DIR`, and `MODEL_DIR`.
5. Define a dictionary `supported_whisper_models` that maps model names to their corresponding `ModelSpec` instances.
6. Define a constant `DEFAULT_MODEL` that refers to the default model to be used, which is the "base.en" model from the `supported_whisper_models` dictionary.

# gcloud.py Pseudocode

1. Import necessary libraries and modules.
2. Define a function `upload_to_gcloud(pdf_path, credentials, bucket_name='session-scribe-bucket')` that:
   - Initializes a Google Cloud Storage client with the provided credentials.
   - Retrieves the specified bucket from the storage client.
   - Creates a blob (object) in the bucket with the same name as the file to be uploaded.    
   - Uploads the file to the created blob.
   - Returns the public URL of the uploaded blob.

# main.py Pseudocode

1. Import necessary libraries and modules.
2. Initialize logger and shared volume.
3. Define the application image with necessary installations.
4. Initialize a stub with the application image.
5. Define a FastAPI application function `fastapi_app()`.
6. Define a function `transcribe_segment(start, end, audio_filepath, model)` that:
   - Creates a temporary file.
   - Trims the audio file to the specified start and end times.
   - Loads the Whisper model.
   - Transcribes the audio file using the model.
   - Adds back offsets to the result.
   - Returns the result.
7. Define a function `transcribe_audio(audio_filepath, result_path, model, unique_id, session_title, presenters)` that:
   - Splits the audio file into segments.
   - Transcribes each segment.
   - Combines the transcriptions.
   - Writes the transcription to a file.
   - Creates a PDF from the transcription.
   - Uploads the PDF to Google Cloud Storage.
   - Upserts the transcript to Supabase.
   - Returns the public URL of the uploaded PDF.
8. Define a function `process_audio(src_url, unique_id, session_title, presenters, is_video, password)` that:
   - Downloads and converts the video to audio if it's a video.
   - Stores the original audio if it's an audio.
   - Calls the `transcribe_audio` function.
   - Deletes the audio file.
   - Returns the public URL of the uploaded PDF.
9. Define a helper function `get_transcript_path(title_slug)` that returns the path of the transcript file.