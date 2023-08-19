# api.py

1. Import necessary libraries and modules.
2. Initialize logger and FastAPI application.
3. Define the `TranscriptionRequest` class which models the request body for the transcription API.
4. Define the `transcribe_and_return_job_id` function which:
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

# logger.py

1. Import necessary libraries and modules.
2. Define a function `get_logger(name, level=logging.INFO)` that sets up and returns a logger with a specified name and logging level.

# constants.py

1. Import necessary libraries and modules.
2. Define a `ModelSpec` dataclass with "name", "params", and "relative_speed" fields.        
3. Define several constants for directory paths, such as `CACHE_DIR`, `RAW_AUDIO_DIR`, `AUDIO_METADATA_DIR`, `TRANSCRIPTIONS_DIR`, and `MODEL_DIR`.
4. Define a dictionary `supported_whisper_models` that maps model names to their corresponding `ModelSpec` instances.
5. Define a constant `DEFAULT_MODEL` that refers to the default model to be used, which is the "base.en" model from the `supported_whisper_models` dictionary.

# gcloud.py

1. Import necessary libraries and modules.
2. Define a function `upload_to_gcloud(pdf_path, credentials, bucket_name='session-scribe-bucket')` that:
   - Initializes a Google Cloud Storage client with the provided credentials.
   - Retrieves the specified bucket from the storage client.
   - Creates a blob (object) in the bucket with the same name as the file to be uploaded.    
   - Uploads the file to the created blob.
   - Returns the public URL of the uploaded blob.

# main.py

1. Import necessary libraries and modules.
2. Initialize logger and shared volume.
3. Define the application image with necessary installations.
4. Initialize a stub with the application image.
5. Define a FastAPI application function `fastapi_app()`. This function is defined within the main.py module.
6. Define a function `transcribe_segment(start, end, audio_filepath, model)` that:
   - Creates a temporary file.
   - Trims the audio file to the specified start and end times using ffmpeg. This task is performed within the main.py module.
   - Loads the Whisper model. This task is performed by the imported whisper module.
   - Transcribes the audio file using the model. This task is performed by the imported whisper module.
   - Adds back offsets to the result. This task is performed within the main.py module.
   - Returns the result.
7. Define a function `transcribe_audio(audio_filepath, result_path, model, unique_id, session_title, presenters)` that:
   - Splits the audio file into segments using the `split_silences` function from the `audio` module. This task is performed by the imported audio module.
   - Transcribes each segment using the `transcribe_segment` function. This task is performed within the main.py module.
   - Combines the transcriptions. This task is performed within the main.py module.
   - Writes the transcription to a file. This task is performed within the main.py module.
   - Creates a PDF from the transcription using the `create_pdf` function from the `pdf` module. This task is performed by the imported pdf module.
   - Uploads the PDF to Google Cloud Storage using the `upload_to_gcloud` function from the `gcloud` module. This task is performed by the imported gcloud module.
   - Upserts the transcript to Supabase using the `supabase_upsert` function from the `supabase` module. This task is performed by the imported supabase module.
   - Returns the public URL of the uploaded PDF.
8. Define a function `process_audio(src_url, unique_id, session_title, presenters, is_video, password)` that:
   - Downloads and converts the video to audio if it's a video using the `download_convert_video_to_audio` function from the `video` module. This task is performed by the imported video module.
   - Stores the original audio if it's an audio using the `store_original_audio` function from the `audio` module. This task is performed by the imported audio module.
   - Calls the `transcribe_audio` function. This task is performed within the main.py module.
   - Deletes the audio file. This task is performed within the main.py module.
   - Returns the public URL of the uploaded PDF.
9. Define a helper function `get_transcript_path(title_slug)` that returns the path of the transcript file. This function is defined within the main.py module.

# pdf.py
1. Import the necessary library (FPDF).
2. Define a function `create_pdf(transcript, title_slug)` that:
   - Initializes a PDF object.
   - Adds a page to the PDF.
   - Sets the font for the PDF.
   - Calculates the maximum width of the cell based on the available page width.
   - Adds a cell with the adjusted width and the transcript text.
   - Saves the PDF with the name `{title_slug}.pdf`.
   - Returns the path of the saved PDF.

# supabase.py
1. Import necessary libraries and modules.
2. Define a function `supabase_upsert(unique_id, session_name, presenters, transcript_text, audio_file_path, transcript_file_path)` that:
   - Initializes a Supabase client with the URL and key from the environment variables.
   - Converts the `audio_file_path` and `transcript_file_path` from PosixPath objects to strings.
   - Gets the current date and time in ISO format.
   - Tries to insert a new row into the 'transcripts' table with the provided data.
   - If an error occurs during the insertion, it raises an exception with the error message.
   - Returns the inserted data if the insertion is successful.

# video.py
1. Import necessary libraries and modules.
2. Define a function `download_convert_video_to_audio(yt_dlp, video_url, password, destination_path)` that:
   - Sets the options for the YoutubeDL object, including the format, postprocessors, video password, and output template.
   - Tries to download the video from the provided URL and convert it to audio.
   - Logs the start and end of the download process.

# test_gcloud.py
1. Import necessary libraries and modules.
2. Load environment variables.
3. Define a function `test_gcloud_upload_and_delete()` that:
   - Loads the Google Cloud credentials from the environment variable.
   - Defines the bucket name.
   - Creates a dummy file for testing.
   - Uploads the dummy file to Google Cloud Storage.
   - Verifies that the file was uploaded correctly by downloading it to a new location.
   - Checks if the content of the downloaded file matches the original.
   - Deletes the file from Google Cloud Storage.
   - Verifies that the file was deleted correctly by attempting to download it again.
   - Cleans up the local dummy files.

# test_pdf.py
1. Import necessary libraries and modules.
2. Load environment variables.
3. Define a function `test_create_pdf_and_print()` that:
   - Prepares the inputs.
   - Calls the `create_pdf` function.
   - Verifies that the PDF file was created.
   - Initializes the Epson Connect client.
   - Prints the PDF and gets the job id.
   - Checks if a job_id was returned.
   - Cleans up the PDF file.

# test_supabase.py
1. Import necessary libraries and modules.
2. Load environment variables.
3. Define a function `test_supabase_upsert()` that:
   - Checks that the Supabase URL and service role are set in the environment variables.
   - Defines the details for the test entry to be inserted.
   - Calls the `supabase_upsert` function.
   - Checks that the returned data matches the inserted entry.
