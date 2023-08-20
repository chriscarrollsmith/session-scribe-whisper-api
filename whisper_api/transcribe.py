import tempfile
import time

import ffmpeg
import torch
import whisper
from modal import Dict, Image, SharedVolume, Stub, asgi_app, Secret
from . import audio, logger, video, gcloud, pdf, supabase
from typing import Optional

@stub.function(
    image=app_image,
    shared_volumes={logger.CACHE_DIR: volume},
    cpu=2,
)
def transcribe_segment(
    start: float,
    end: float,
    audio_filepath: pathlib.Path,
    model: logger.ModelSpec,
):
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
            model.name, device=device, download_root=logger.MODEL_DIR
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
