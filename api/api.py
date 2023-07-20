from fastapi import FastAPI, HTTPException
from . import config
from .main import process_audio

logger = config.get_logger(__name__)
web_app = FastAPI()

@web_app.post("/api/transcribe")
async def transcribe_and_return_url(
    src_url: str, title_slug: str, is_video: bool = False, password: str = None
):
    try:
        # Transcribe the audio
        call = process_audio.spawn(src_url, title_slug, is_video, password)
        
        # If the process_audio function call fails, it would raise an exception,
        # so there's no need to check call.failed
        
        # process_audio returns the URL to the transcription
        transcription_url = call.get_result()

        return {"transcription_url": transcription_url}
    
    except Exception as e:
        # An unexpected error occurred, return a 500 error
        logger.error(f"An unexpected error occurred while transcribing: {str(e)}")
        raise HTTPException(
            status_code=500,  # Internal Server Error
            detail=f"An unexpected error occurred while transcribing: {str(e)}"
        )
