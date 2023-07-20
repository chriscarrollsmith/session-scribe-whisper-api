import os
from api import pdf
import epson_connect
from dotenv import load_dotenv

load_dotenv()

def test_create_pdf_and_print():
    # Prepare the inputs
    transcript = "This is a test transcript."
    title_slug = "test_transcript"

    # Call the function
    pdf_path = pdf.create_pdf(transcript, title_slug)

    # Verify that the file was created
    assert os.path.exists(pdf_path)

    # Initialize the Epson Connect client
    ec = epson_connect.Client()

    # Print the PDF and get the job id
    job_id = ec.printer.print(pdf_path)

    # Check if a job_id was returned
    assert job_id is not None

    # Cleanup the PDF file
    os.remove(pdf_path)
