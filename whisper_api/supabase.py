from supabase import create_client
from datetime import datetime
import pytz
import os

def supabase_upsert(unique_id: str, session_name: str, presenters: str, transcript_text: str, audio_file_path: str, transcript_file_path: str):
    # Initialize Supabase client
    url: str = os.getenv(key="SUPABASE_URL")
    key: str = os.getenv(key="SUPABASE_SERVICE_ROLE")
    supabase = create_client(supabase_url=url, supabase_key=key)
    
    # Convert PosixPath objects to strings
    audio_file_path = str(audio_file_path)
    transcript_file_path = str(transcript_file_path)
    
    utc_now = datetime.now(pytz.utc)
    created_at = utc_now.isoformat()

    try:
        data, count = supabase.table(table_name='transcripts') \
            .insert(json=[
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
        raise Exception(str(object=e))

def supabase_delete(unique_id: str) -> tuple[str, any]:
    # Initialize Supabase client
    url: str = os.getenv(key="SUPABASE_URL")
    key: str = os.getenv(key="SUPABASE_SERVICE_ROLE")
    supabase = create_client(supabase_url=url, supabase_key=key)

    try:
        # Delete the record matching the unique_id from the 'transcripts' table
        data, count = supabase.table(table_name='transcripts') \
            .delete() \
            .eq(column='id', value=unique_id) \
            .execute()

        return data
    except Exception as e:
        raise Exception(str(e))