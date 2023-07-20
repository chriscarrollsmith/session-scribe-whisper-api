from fpdf import FPDF

def create_pdf(transcript, title_slug):
    pdf = FPDF()

    # Add a page
    pdf.add_page()

    # Set font
    pdf.set_font("Arial", size = 15)

    # Add a cell
    pdf.cell(200, 10, txt = transcript, ln = True, align = 'C')

    # Save the pdf with name .pdf
    pdf_path = f"{title_slug}.pdf"
    pdf.output(pdf_path)

    return pdf_path