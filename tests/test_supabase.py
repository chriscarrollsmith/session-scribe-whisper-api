from whisper_api import supabase  # replace with the actual module name
from dotenv import load_dotenv
import os

load_dotenv()

def test_supabase_upsert():

    assert os.getenv("SUPABASE_URL") is not None
    assert os.getenv("SUPABASE_SERVICE_ROLE") is not None

    # These are the details for the test entry to be inserted
    unique_id = 9223372036854
    session_name = "Test Session"
    presenters = "Test Presenters"
    transcript_text = "Test transcript"
    audio_file_path = "/path/to/audio/file"
    transcript_file_path = "/path/to/transcript/file"

    # Call the function
    data = supabase.supabase_upsert(unique_id, session_name, presenters, transcript_text, audio_file_path, transcript_file_path)

    # Check that the returned data matches the inserted entry
    # This assumes that the returned data includes the inserted entry
    assert data is not None

    # Now, you would usually verify that the data has been inserted in the database.
    # However, please note that this may not always be feasible or recommended, 
    # especially if the database is used in a production environment.
