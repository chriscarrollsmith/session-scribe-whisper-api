import tempfile
import time
import pathlib
import ffmpeg
import torch
import whisper
from . import logger
from .constants import ModelSpec, MODEL_DIR

logger = logger.get_logger(name=__name__)


def transcribe_segment(
    start: float,
    end: float,
    audio_filepath: pathlib.Path,
    model: ModelSpec,
):
    t0 = time.time()
    with tempfile.NamedTemporaryFile(suffix=".mp3") as f:
        (
            ffmpeg.input(filename=str(object=audio_filepath))
            .filter("atrim", start=start, end=end)
            .output(f.name)
            .overwrite_output()
            .run(quiet=True)
        )

        use_gpu = torch.cuda.is_available()
        device = "cuda" if use_gpu else "cpu"
        model = whisper.load_model(
            name=model.name, device=device, download_root=MODEL_DIR
        )
        result = model.transcribe(f.name, language="en", fp16=use_gpu)  # type: ignore

    logger.info(
        msg=f"Transcribed segment {start:.2f} to {end:.2f} of {end - start:.2f} in {time.time() - t0:.2f} seconds."
    )

    # Add back offsets
    for segment in result["segments"]:
        segment["start"] += start
        segment["end"] += start

    return result
