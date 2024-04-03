import pypdfium2 as pdfium  # Ensure you have version 4.20.0 installed
import numpy as np
from PIL import Image
import io
import tempfile


def extract_images_from_pdf_bytes(pdf_bytes):
    images = []  # To store extracted images

    # Create a temporary file to write the PDF bytes
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        tmpfile.write(pdf_bytes)
        tmpfile_path = tmpfile.name

    # Load the PDF from the temporary file path
    pdf = pdfium.PdfDocument(tmpfile_path)

    # Iterate through each page
    for page_number in range(len(pdf)):
        page = pdf.get_page(page_number)

        # For demonstration, we render the whole page as an image
        # Note: This does not extract embedded images directly
        image = page.render_topil()
        images.append(image)

    # Optionally, save or process the images
    # For example, save the first image (if exists)
    if images:
        images[0].save("extracted_image_0.png")

    return images


# Example usage
# pdf_bytes = b'your_pdf_bytes_here'
# images = extract_images_from_pdf_bytes(pdf_bytes)
