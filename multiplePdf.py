import PyPDF2
from io import BytesIO

def combine_pdfs(pdf_bytes_list):
    pdf_writer = PyPDF2.PdfWriter()

    for pdf_bytes in pdf_bytes_list:
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            pdf_writer.add_page(page)

    combined_pdf = BytesIO()
    pdf_writer.write(combined_pdf)
    combined_pdf.seek(0)
    breakpoint()
    return combined_pdf.getvalue()

# Example usage:
pdf_bytes_list = []
file_names = ["1111.pdf", "1111.pdf", "1111.pdf", "1111.pdf"]  # Add your PDF files here

for file_name in file_names:
    with open(file_name, "rb") as file:
        pdf_bytes_list.append(file.read())

combined_pdf_bytes = combine_pdfs(pdf_bytes_list)

# Save the combined PDF to a file
with open("combined_pdf.pdf", "wb") as f:
    f.write(combined_pdf_bytes)
