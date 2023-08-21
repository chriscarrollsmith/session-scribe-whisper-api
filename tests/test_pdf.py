import os
from whisper_api import pdf
from dotenv import load_dotenv

load_dotenv()

def test_create_pdf_and_print() -> None:
    # Prepare the inputs
    transcript = "This is a test transcript."
    title_slug = "test_transcript"

    # Call the function
    pdf_path = pdf.create_pdf(transcript=transcript, title_slug=title_slug)

    # Verify that the file was created
    assert os.path.exists(path=pdf_path)

    # Cleanup the PDF file
    os.remove(path=pdf_path)
