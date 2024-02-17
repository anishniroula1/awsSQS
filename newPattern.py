from PyPDF2 import PdfReader, PdfWriter
import io
from pdf2image import convert_from_bytes

# Assuming `pdf_bytes` is the byte content of your PDF file
pdf_bytes = b'your_pdf_bytes_here'

# Load the PDF from bytes using PdfReader
pdf_reader = PdfReader(io.BytesIO(pdf_bytes))

# This will store the output images
images = []

# Convert each page to an image
for page in range(len(pdf_reader.pages)):
    # For `pdf2image`, we need to convert each page back to bytes
    page_bytes = io.BytesIO()
    pdf_writer = PdfWriter()
    pdf_writer.add_page(pdf_reader.pages[page])
    pdf_writer.write(page_bytes)
    page_bytes.seek(0)  # Go back to the start of the BytesIO object
    
    # Now convert this single-page PDF bytes to an image
    page_images = convert_from_bytes(page_bytes.getvalue(), dpi=200)
    images.extend(page_images)
