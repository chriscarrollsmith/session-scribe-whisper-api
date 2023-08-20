import dataclasses
import pathlib

@dataclasses.dataclass
class ModelSpec:
    name: str
    params: str
    relative_speed: int  # Higher is faster

CACHE_DIR = "/cache"
RAW_AUDIO_DIR = pathlib.Path(CACHE_DIR, "raw_audio")
# Stores metadata of individual audio as JSON.
AUDIO_METADATA_DIR = pathlib.Path(CACHE_DIR, "audio_metadata")
# Completed episode transcriptions. Stored as flat files with
# files structured as '{title_slug}.json'.
TRANSCRIPTIONS_DIR = pathlib.Path(CACHE_DIR, "transcriptions")
# Location of modal checkpoint.
MODEL_DIR = pathlib.Path(CACHE_DIR, "model")
# Audio splitting parameters
SILENCE_DB = "-10dB"
MIN_SEGMENT_LENGTH = 30.0
MIN_SILENCE_LENGTH = 1.0

supported_whisper_models = {
    "tiny.en": ModelSpec(name="tiny.en", params="39M", relative_speed=32),
    # Takes around 3-10 minutes to transcribe a audio, depending on length.
    "base.en": ModelSpec(name="base.en", params="74M", relative_speed=16),
    "small.en": ModelSpec(name="small.en", params="244M", relative_speed=6),
    "medium.en": ModelSpec(name="medium.en", params="769M", relative_speed=2),
    # Very slow. Will take around 45 mins to 1.5 hours to transcribe.
    "large": ModelSpec(name="large", params="1550M", relative_speed=1),
}

DEFAULT_MODEL = supported_whisper_models["base.en"]
