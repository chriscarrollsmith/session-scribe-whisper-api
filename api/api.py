from fastapi import FastAPI, HTTPException
from . import config
from .main import process_audio
from typing import Optional

logger = config.get_logger(__name__)
web_app = FastAPI()

@web_app.post("/api/transcribe")
async def transcribe_and_return_job_id(
    src_url: str, unique_id: int, session_title: Optional[str] = None, presenters: Optional[str] = None, is_video: bool = False, password: str = None
):
    try:
        # Transcribe the audio
        call = process_audio.spawn(src_url, unique_id, session_title, presenters, is_video, password)
        
        # Assuming `call` has an 'object_id' attribute to track the job
        job_id = call.object_id

        return {"job_id": job_id}
    
    except Exception as e:
        # An unexpected error occurred, return a 500 error
        logger.error(f"An unexpected error occurred while transcribing: {str(e)}")
        raise HTTPException(
            status_code=500,  # Internal Server Error
            detail=f"An unexpected error occurred while transcribing: {str(e)}"
        )
