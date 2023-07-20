from supabase import create_client
from datetime import datetime
import os

def supabase_upsert(unique_id: str, session_name: str, presenters: str, transcript_text: str, audio_file_path: str, transcript_file_path: str):
    # Initialize Supabase client
    url: str = os.getenv("SUPABASE_URL")
    key: str = os.getenv("SUPABASE_SERVICE_ROLE")
    supabase = create_client(url, key)
    
    # Convert PosixPath objects to strings
    audio_file_path = str(audio_file_path)
    transcript_file_path = str(transcript_file_path)
    
    created_at = datetime.now().isoformat()

    try:
        data, count = supabase.table('transcripts') \
            .insert([
                {
                    'id': unique_id,
                    'created_at': created_at,
                    'session_name': session_name,
                    'presenters': presenters,
                    'transcript': transcript_text,
                    'audio_file_path': audio_file_path,
                    'transcript_file_path': transcript_file_path
                },
            ]) \
            .execute()

        return data
    except Exception as e:
        raise Exception(str(e))
