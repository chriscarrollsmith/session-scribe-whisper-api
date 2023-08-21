"""
Uses OpenAI's Whisper API to do speech-to-text transcription
of audio, and Modal for easy containerized deployment of the app.
"""
from . import audio, logger, video, gcloud, pdf, supabase, transcribe
from .constants import ( CACHE_DIR, DEFAULT_MODEL, MODEL_DIR, RAW_AUDIO_DIR,
                        TRANSCRIPTIONS_DIR )
import json
import os
import pathlib
from typing import Optional
from fastapi import FastAPI
from modal import Dict, Image, NetworkFileSystem, Stub, asgi_app, Secret
import dacite
import whisper
import yt_dlp
from google.oauth2 import service_account

logger = logger.get_logger(name=__name__)

# Create a persistent cache for storing logs across application runs
volume = NetworkFileSystem.persisted(label="dataset-cache-vol")

app_image = (
    Image.debian_slim(python_version="3.11")
    .pip_install(
        "numba>=0.57.1",
        "fastapi",
        "pydantic>=2.2.1",
        "openai-whisper",
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
        "supabase>=1.0.3"
    )
    .apt_install("ffmpeg")
    .pip_install("ffmpeg-python")
)

# Create a modal.Stub instance for managing the application
stub = Stub(
    name="whisper-audio-video-transcriber-api-v2",
    image=app_image,
)

# Define a dictionary object for tracking progress within the Stub
stub.in_progress = Dict.new()

# Import api.py and register it with the stub as an asynchronous ASGI app,
# including setting shared volumes and a keep-warm strategy
@stub.function(
    network_file_systems={CACHE_DIR: volume},
    keep_warm=1
)
@asgi_app()
def fastapi_app() -> FastAPI:
    from .api import web_app
    return web_app


# Register the process_audio function with the stub, along with specific
# configurations like image, shared volumes, secrets, etc.
# This function controls the overall flow of the application.
@stub.function(
    image=app_image,
    network_file_systems={CACHE_DIR: volume},
    timeout=900,
    secrets=[
        Secret.from_name(app_name="my-googlecloud-secret"),
        Secret.from_name(app_name="supabase")
    ]
)
def process_audio(src_url: str, unique_id: int, session_title: Optional[str] = None, presenters: Optional[str] = None, is_video: bool=False, password: str=None) -> None:    
    # Get the title slug from the unique_id
    title_slug = str(object=unique_id)

    # Get working file paths from the slug
    destination_path: pathlib.Path = RAW_AUDIO_DIR / title_slug
    audio_filepath: pathlib.Path = f"{destination_path}.mp3" if is_video else destination_path
    transcription_path: pathlib.Path = TRANSCRIPTIONS_DIR / f"{title_slug}.json"

    try:
        # pre-download the model to the cache path, because the _download fn is not
        # thread-safe and can cause issues when multiple requests are made at the same time.
        model = DEFAULT_MODEL
        whisper._download(url=whisper._MODELS[model.name], root=MODEL_DIR, in_memory=False)

        RAW_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
        TRANSCRIPTIONS_DIR.mkdir(parents=True, exist_ok=True)

        if is_video:
            video.download_convert_video_to_audio(
                yt_dlp=yt_dlp,
                video_url=src_url,
                password=password,
                destination_path=destination_path
            )
        else:
            audio.store_original_audio(
                url=src_url,
                destination=destination_path,
            )

        # Upload the media file to Gcloud and get the public url
        public_audio_url = gcloud.upload_to_gcloud(path=audio_filepath, credentials=credentials)

        logger.info(
            msg=f"Using the {model.name} model which has {model.params} parameters."
        )

        segment_gen = audio.split_silences(path=str(audio_filepath))

        output_text = ""
        output_segments = []
        for result in transcribe_segment_wrapper.starmap(
            segment_gen, kwargs=dict(audio_filepath=audio_filepath, model=model)
        ):
            output_text += result["text"]
            output_segments += result["segments"]

        result = {
            "text": output_text,
            "segments": output_segments,
            "language": "en",
        }

        logger.info(msg=f"Writing openai/whisper transcription to {transcription_path}")
        with open(file=transcription_path, mode="w") as f:
            json.dump(obj=result, fp=f, indent=4)

        # Create a PDF
        pdf_path = pdf.create_pdf(transcript=output_text, title_slug=title_slug)

        # Load the secret and use it for authenticating with Google Cloud Storage
        service_account_info = json.loads(s=os.environ["SERVICE_ACCOUNT_JSON"])
        credentials = service_account.Credentials.from_service_account_info(info=service_account_info)

        # Upload the PDF to Gcloud and get the public url
        public_pdf_url = gcloud.upload_to_gcloud(path=pdf_path, credentials=credentials)

        # Upsert the transcript to Supabase
        supabase.supabase_upsert(unique_id=unique_id, session_name=session_title if session_title else title_slug, presenters=presenters if presenters else "Unknown", transcript_text=output_text, audio_file_path=public_audio_url, transcript_file_path=public_pdf_url)

    except Exception as e:
        logger.exception(msg=e)
        raise dacite.DaciteError("Failed to process audio") from e

    finally:
        # Delete the audio file
        if audio_filepath and os.path.exists(path=audio_filepath):
            logger.info(msg=f"Deleting the audio file in '{audio_filepath}'")
            os.remove(path=audio_filepath)
            logger.info(msg=f"Deleted the audio file in '{audio_filepath}'")

        # Delete the transcription file
        if transcription_path and os.path.exists(path=transcription_path):
            logger.info(msg=f"Deleting the transcription file at '{transcription_path}'")
            os.remove(path=transcription_path)
            logger.info(msg=f"Deleted the transcription file at '{transcription_path}'")

        # Delete the PDF file
        if pdf_path and os.path.exists(path=pdf_path):
            logger.info(msg=f"Deleting the PDF file at '{pdf_path}'")
            os.remove(path=pdf_path)
            logger.info(msg=f"Deleted the PDF file at '{pdf_path}'")


# Register the transcribe_segment function with the stub
@stub.function(
    image=app_image,
    network_file_systems={CACHE_DIR: volume},
    cpu=2
)
def transcribe_segment_wrapper(*args, **kwargs):
    return transcribe.transcribe_segment(*args, **kwargs)
