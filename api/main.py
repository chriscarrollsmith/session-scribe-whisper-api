"""
Uses OpenAI's Whisper modal to do speech-to-text transcription
of audio.
"""
import json
import os
import pathlib
from google.oauth2 import service_account
from modal import Dict, Image, SharedVolume, Stub, asgi_app, Secret
from . import audio, config, video, gcloud, pdf

#from dotenv import load_dotenv
#load_dotenv()

logger = config.get_logger(__name__)
volume = SharedVolume().persist("dataset-cache-vol")

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
        "google-cloud-storage"
    )
    .apt_install("ffmpeg")
    .pip_install("ffmpeg-python")
)

stub = Stub(
    "whisper-audio-video-transcriber-api-v2",
    image=app_image,
)

stub.in_progress = Dict()


@stub.function(
    shared_volumes={config.CACHE_DIR: volume},
    keep_warm=1,
)
@asgi_app()
def fastapi_app():
    from .api import web_app

    return web_app


@stub.function(
    image=app_image,
    shared_volumes={config.CACHE_DIR: volume},
    cpu=2,
)
def transcribe_segment(
    start: float,
    end: float,
    audio_filepath: pathlib.Path,
    model: config.ModelSpec,
):
    import tempfile
    import time

    import ffmpeg
    import torch
    import whisper

    t0 = time.time()
    with tempfile.NamedTemporaryFile(suffix=".mp3") as f:
        (
            ffmpeg.input(str(audio_filepath))
            .filter("atrim", start=start, end=end)
            .output(f.name)
            .overwrite_output()
            .run(quiet=True)
        )

        use_gpu = torch.cuda.is_available()
        device = "cuda" if use_gpu else "cpu"
        model = whisper.load_model(
            model.name, device=device, download_root=config.MODEL_DIR
        )
        result = model.transcribe(f.name, language="en", fp16=use_gpu)  # type: ignore

    logger.info(
        f"Transcribed segment {start:.2f} to {end:.2f} of {end - start:.2f} in {time.time() - t0:.2f} seconds."
    )

    # Add back offsets.
    for segment in result["segments"]:
        segment["start"] += start
        segment["end"] += start

    return result


@stub.function(
    image=app_image,
    shared_volumes={config.CACHE_DIR: volume},
    timeout=900,
    secret=Secret.from_name("my-googlecloud-secret"),
)
def transcribe_audio(
    audio_filepath: pathlib.Path,
    result_path: pathlib.Path,
    model: config.ModelSpec
):
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

    logger.info(f"Writing openai/whisper transcription to {result_path}")
    with open(result_path, "w") as f:
        json.dump(result, f, indent=4)

    # Get the title slug from the audio file path
    title_slug = os.path.basename(audio_filepath).rsplit('.', 1)[0]

    # Create a PDF
    pdf_path = pdf.create_pdf(output_text, title_slug)

    # Load the secret and use it for authenticating with Google Cloud Storage
    service_account_info = json.loads(os.environ["SERVICE_ACCOUNT_JSON"])
    credentials = service_account.Credentials.from_service_account_info(service_account_info)

    # Upload the PDF to Gcloud and get the public url
    public_url = gcloud.upload_to_gcloud(pdf_path, credentials)

    return public_url


@stub.function(
    image=app_image,
    shared_volumes={config.CACHE_DIR: volume},
    timeout=900,
)
def process_audio(src_url: str, title_slug: str, is_video: bool, password: str):
    import dacite
    import whisper
    import yt_dlp

    destination_path = config.RAW_AUDIO_DIR / title_slug

    # Video files are converted to mp3, so we need to pass the mp3 file path.
    audio_filepath = f"{destination_path}.mp3" if is_video else destination_path

    try:
        transcription_path = get_transcript_path(title_slug)

        # pre-download the model to the cache path, because the _download fn is not
        # thread-safe.
        model = config.DEFAULT_MODEL
        whisper._download(whisper._MODELS[model.name], config.MODEL_DIR, False)

        config.RAW_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
        config.TRANSCRIPTIONS_DIR.mkdir(parents=True, exist_ok=True)

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

        public_url = transcribe_audio.call(
            audio_filepath=audio_filepath,
            result_path=transcription_path,
            model=model,
        )
    except Exception as e:
        logger.exception(e)
        raise dacite.DaciteError("Failed to process audio") from e

    finally:
        logger.info(f"Deleting the audio file in '{destination_path}'")
        os.remove(audio_filepath)
        logger.info(f"Deleted the audio file in '{destination_path}'")

    return public_url  # return the public URL of the uploaded PDF


def get_transcript_path(title_slug: str) -> pathlib.Path:
    return config.TRANSCRIPTIONS_DIR / f"{title_slug}.json"