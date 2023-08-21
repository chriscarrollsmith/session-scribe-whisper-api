"""
Uses OpenAI's Whisper API to do speech-to-text transcription
of audio, and Modal for easy containerized deployment of the app.
"""
import json
import os
import pathlib
from google.oauth2 import service_account
from modal import Dict, Image, NetworkFileSystem, Stub, asgi_app, Secret
from . import audio, logger, video, gcloud, pdf, supabase
from .transcribe import transcribe_segment
from .constants import ( CACHE_DIR, DEFAULT_MODEL, MODEL_DIR, RAW_AUDIO_DIR, TRANSCRIPTIONS_DIR )
from typing import Optional

logger = logger.get_logger(__name__)

# Create a persistent cache for storing logs across application runs
volume = NetworkFileSystem().persisted(label="dataset-cache-vol")

app_image = (
    Image.debian_slim()
    .pip_install(
        "https://github.com/openai/whisper/archive/9f70a352f9f8630ab3aa0d06af5cb9532bd8c21d.tar.gz",
        "dacite",
        "jiwer",
        "gql[all]~=3.0.0a5",
        "pandas",
        "loguru==0.6.0",
        "torchaudio",
        "yt-dlp",
        "fpdf",
        "google-cloud-storage",
        "pytz",
        "supabase"
    )
    .apt_install("ffmpeg")
    .pip_install("ffmpeg-python")
)

# Create a modal.Stub instance for managing the application
stub = Stub(
    "whisper-audio-video-transcriber-api-v2",
    image=app_image,
)

# Define a dictionary object for tracking progress within the Stub
stub.in_progress = Dict()

# Import api.py and register it with the stub as an asynchronous ASGI app,
# including setting shared volumes and a keep-warm strategy
@stub.function(
    shared_volumes={CACHE_DIR: volume},
    keep_warm=1,
)
@asgi_app()
def fastapi_app():
    from .api import web_app
    return web_app

# Register the process_audio function with the stub, along with specific
# configurations like image, shared volumes, secrets, etc.
# This function controls the overall flow of the application.
@stub.function(
    image=app_image,
    shared_volumes={CACHE_DIR: volume},
    timeout=900,
    secrets=[
        Secret.from_name("my-googlecloud-secret"),
        Secret.from_name("supabase")
    ]
)
def process_audio(src_url: str, unique_id: int, session_title: Optional[str] = None, presenters: Optional[str] = None, is_video: bool=False, password: str=None):
    import dacite
    import whisper
    import yt_dlp

    # Get the title slug from the unique_id
    title_slug = str(unique_id)

    destination_path = RAW_AUDIO_DIR / title_slug

    # Video files are converted to mp3, so we need to pass the mp3 file path.
    audio_filepath = f"{destination_path}.mp3" if is_video else destination_path

    try:
        transcription_path = get_transcript_path(title_slug)

        # pre-download the model to the cache path, because the _download fn is not
        # thread-safe and can cause issues when multiple requests are made at the same time.
        model = DEFAULT_MODEL
        whisper._download(whisper._MODELS[model.name], MODEL_DIR, False)

        RAW_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
        TRANSCRIPTIONS_DIR.mkdir(parents=True, exist_ok=True)

        if is_video:
            video.download_convert_video_to_audio(
                yt_dlp, src_url, password, destination_path
            )
        else:
            audio.store_original_audio(
                url=src_url,
                destination=destination_path,
            )

        logger.info(
            f"Using the {model.name} model which has {model.params} parameters."
        )

        segment_gen = audio.split_silences(str(audio_filepath))

        output_text = ""
        output_segments = []
        for result in transcribe_segment.starmap(
            segment_gen, kwargs=dict(audio_filepath=audio_filepath, model=model)
        ):
            output_text += result["text"]
            output_segments += result["segments"]

        result = {
            "text": output_text,
            "segments": output_segments,
            "language": "en",
        }

        logger.info(f"Writing openai/whisper transcription to {transcription_path}")
        with open(transcription_path, "w") as f:
            json.dump(result, f, indent=4)

        # Create a PDF
        pdf_path = pdf.create_pdf(output_text, title_slug)

        # Load the secret and use it for authenticating with Google Cloud Storage
        service_account_info = json.loads(os.environ["SERVICE_ACCOUNT_JSON"])
        credentials = service_account.Credentials.from_service_account_info(service_account_info)

        # Upload the PDF to Gcloud and get the public url
        public_url = gcloud.upload_to_gcloud(pdf_path, credentials)

        # Upsert the transcript to Supabase
        supabase.supabase_upsert(unique_id, session_title if session_title else title_slug, presenters if presenters else "Unknown", output_text, audio_filepath, public_url)

    except Exception as e:
        logger.exception(e)
        raise dacite.DaciteError("Failed to process audio") from e

    finally:
        logger.info(f"Deleting the audio file in '{destination_path}'")
        os.remove(audio_filepath)
        logger.info(f"Deleted the audio file in '{destination_path}'")

    return public_url  # return the public URL of the uploaded PDF


def get_transcript_path(title_slug: str) -> pathlib.Path:
    return TRANSCRIPTIONS_DIR / f"{title_slug}.json"
