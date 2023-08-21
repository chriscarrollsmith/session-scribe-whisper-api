from whisper_api import supabase
from dotenv import load_dotenv
import datetime
import os

load_dotenv()

def test_supabase_upsert() -> None:

    assert os.getenv(key="SUPABASE_URL") is not None
    assert os.getenv(key="SUPABASE_SERVICE_ROLE") is not None

    # These are the details for the test entry to be inserted
    unique_id = 9223372036854
    session_name = "Test Session"
    presenters = "Test Presenters"
    transcript_text = "Test transcript"
    audio_file_path = "/path/to/audio/file"
    transcript_file_path = "/path/to/transcript/file"

    # Call the function
    data = supabase.supabase_upsert(unique_id=unique_id, session_name=session_name, presenters=presenters, transcript_text=transcript_text, audio_file_path=audio_file_path, transcript_file_path=transcript_file_path)

    try:
        # Check that the returned data matches the inserted entry
        assert data is not None
        assert data[1][0]['id'] == unique_id
        assert data[1][0]["session_name"] == session_name
        assert data[1][0]["presenters"] == presenters
        assert data[1][0]["transcript"] == transcript_text
        assert data[1][0]["audio_file_path"] == audio_file_path
        assert data[1][0]["transcript_file_path"] == transcript_file_path

        # Check that created_at contains today's date and a plus sign
        created_at_str = data[1][0]["created_at"]
        assert created_at_str is not None
        assert created_at_str[0:10] == datetime.date.today().isoformat()
        assert "+" in created_at_str
    finally:
        # Remove the test entry
        supabase.supabase_delete(unique_id=unique_id)