from fastapi import FastAPI, Body, HTTPException
from . import config
from .main import process_audio
from typing import Optional
from pydantic import BaseModel

logger = config.get_logger(__name__)
web_app = FastAPI()

# Function removed

class TranscriptionRequest(BaseModel):
    src_url: str
    unique_id: int
    session_title: Optional[str] = None
    presenters: Optional[str] = None
    is_video: Optional[bool] = False
    password: Optional[str] = None

@web_app.post("/api/transcribe")
async def transcribe_and_return_job_id(
    request: TranscriptionRequest = Body(...)
):
    try:
        # Transcribe the audio
        call = process_audio.spawn(**request.dict())
        
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
