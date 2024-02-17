import requests
from dotenv import load_dotenv

load_dotenv()

def test_transcribe_endpoint() -> None:
    # Define the URL
    url = os.environ["MODAL_DOMAIN] + '/api/transcribe'

    # Define the headers
    headers = {
        'Content-Type': 'application/json',
    }

    # Define the payload
    data = {
        "src_url": "https://storage.googleapis.com/" + os.environ["BUCKET_NAME] + "/1689897654847-audio-1689897655558.mp3",
        "unique_id": 987654,
        "session_title": "Session Title Here",
        "presenters": "Presenters Here",
        "is_video": False
    }

    # Make the POST request
    response = requests.post(url=url, json=data, headers=headers)

    # Assert that the response code is 200
    assert response.status_code == 200
