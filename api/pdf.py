from fpdf import FPDF

def create_pdf(transcript, title_slug):
    pdf = FPDF()

    # Add a page
    pdf.add_page()

    # Set font
    pdf.set_font("Arial", size=15)

    # Get the available page width
    page_width = pdf.w - 2 * pdf.l_margin

    # Calculate the maximum width of the cell based on available page width
    max_cell_width = page_width - 2 * pdf.c_margin

    # Add a cell with adjusted width
    pdf.multi_cell(max_cell_width, 10, txt=transcript, align='C')

    # Save the pdf with name .pdf
    pdf_path = f"{title_slug}.pdf"
    pdf.output(pdf_path)

    return pdf_path
