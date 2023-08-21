# Import necessary libraries and modules
import dataclasses
import pathlib
import urllib.request
from typing import NamedTuple, TypedDict, Iterator, Tuple
import re
import ffmpeg
from . import logger
from .constants import SILENCE_DB, MIN_SEGMENT_LENGTH, MIN_SILENCE_LENGTH

# Get logger instance
logger = logger.get_logger(name=__name__)

# Define Segment type
Segment = TypedDict("Segment", {"text": str, "start": float, "end": float})

# Define AudioMetadata as a dataclass
@dataclasses.dataclass
class AudioMetadata:
    title_slug: str
    audio_url: str

# Define DownloadResult as a NamedTuple
class DownloadResult(NamedTuple):
    data: bytes
    # Helpful to store and transmit when uploading to cloud bucket.
    content_type: str

# Function to download audio file from a given URL
def download_audio_file(url: str) -> DownloadResult:
    # Create a request object with headers to avoid
    req = urllib.request.Request(
        url=url,
        data=None,
        # Set a user agent to avoid 403 response from some audio audio servers.
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
        },
    )
    # Open the URL and return the response data and content type
    with urllib.request.urlopen(url=req) as response:
        return DownloadResult(
            data=response.read(),
            content_type=response.headers["content-type"],
        )

# Function to format file size in human readable format
def format_file_size(num, suffix="B") -> str:
    # Loop through units and format the size
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, "Yi", suffix)


# Function to store original audio file
def store_original_audio(
    url: str, destination: pathlib.Path, overwrite: bool = False
) -> None:
    # Check if the destination file already exists
    if destination.exists():
        if overwrite:
            logger.info(
                msg=f"Audio file exists at {destination} but overwrite option is specified."
            )
        else:
            logger.info(msg=f"Audio file exists at {destination}, skipping download.")
            return

    # Download the audio file from the URL
    audio_download_result = download_audio_file(url=url)
    humanized_bytes_str = format_file_size(num=len(audio_download_result.data))
    logger.info(msg=f"Downloaded {humanized_bytes_str} audio from URL.")
    
    # Write the downloaded data to the destination file
    with open(file=destination, mode="wb") as f:
        f.write(audio_download_result.data)
    logger.info(msg=f"Stored audio at {destination}.")


# Function to combine short transcript segments
def coalesce_short_transcript_segments(
    segments: list[Segment],
) -> list[Segment]:
    """
    Some extracted transcript segments from openai/whisper are really short, like even just one word.
    This function accepts a minimum segment length and combines short segments until the minimum is reached.
    """
    # Set minimum transcript length to 200 characters
    minimum_transcript_len = 200  # About 2 sentences.
    previous = None
    long_enough_segments = []
    # Loop through segments and combine short segments until the minimum is reached
    for current in segments:
        if previous is None:
            previous = current
        elif len(previous["text"]) < minimum_transcript_len:
            previous = _combine_segments(left=previous, right=current)
        else:
            long_enough_segments.append(previous)
            previous = current
    if previous:
        long_enough_segments.append(previous)
    return long_enough_segments


# Function to combine two segments
def _combine_segments(left: Segment, right: Segment) -> Segment:
    return {
        "text": left["text"] + " " + right["text"],
        "start": left["start"],
        "end": right["end"],
    }


# Function to split audio file into contiguous chunks using the ffmpeg `silencedetect` filter
def split_silences(
    path: str, min_segment_length: float = MIN_SEGMENT_LENGTH, min_silence_length: float = MIN_SILENCE_LENGTH
) -> Iterator[Tuple[float, float]]:
    """Split audio file into contiguous chunks using the ffmpeg `silencedetect` filter.
    Yields tuples (start, end) of each chunk in seconds."""

    # Define regex to match silence end and duration
    silence_end_re = re.compile(
        pattern=r" silence_end: (?P<end>[0-9]+(\.?[0-9]*)) \| silence_duration: (?P<dur>[0-9]+(\.?[0-9]*))"
    )

    # Get metadata of the audio file
    metadata = ffmpeg.probe(filename=path)
    duration = float(__x=metadata["format"]["duration"])

    # Create a ffmpeg reader object
    reader = (
        ffmpeg.input(filename=str(path))
        .filter("silencedetect", n=SILENCE_DB, d=min_silence_length)
        .output("pipe:", format="null")
        .run_async(pipe_stderr=True)
    )

    # Loop through the reader object and yield the start and end of each chunk
    cur_start = 0.0
    num_segments = 0
    while True:
        line = reader.stderr.readline().decode("utf-8")
        if not line:
            break
        match = silence_end_re.search(string=line)
        if match:
            silence_end, silence_dur = match.group("end"), match.group("dur")
            split_at = float(silence_end) - (float(silence_dur) / 2)

            if (split_at - cur_start) < min_segment_length:
                continue

            yield cur_start, split_at
            cur_start = split_at
            num_segments += 1

    # silencedetect can place the silence end *after* the end of the full audio segment.
    # Such segment definitions are negative length and invalid.
    # If the last segment is invalid, drop it.
    if duration > cur_start and (duration - cur_start) > min_segment_length:
        yield cur_start, duration
        num_segments += 1
    logger.info(msg=f"Split {path} into {num_segments} segments")
