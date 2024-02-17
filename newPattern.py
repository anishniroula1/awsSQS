import pypdfium2 as pdfium  # Make sure you have version 4.20.0 installed
import numpy as np
from PIL import Image
import io

def extract_images_from_pdf_bytes(pdf_bytes):
    # Load the PDF from bytes
    pdf = pdfium.PdfDocument.from_bytes(pdf_bytes)
    
    images = []  # To store extracted images

    # Iterate through each page
    for page_number in range(len(pdf)):
        page = pdf.get_page(page_number)
        
        # Render page to a numpy array
        pix = page.render_topil()
        
        # Extract images (this example simply renders the page, further extraction would be required for individual images)
        # For demonstration, let's consider the rendered page as an "image"
        images.append(pix)

    # Optionally, save or process the images
    # For example, save the first image (if exists)
    if images:
        images[0].save("extracted_image_0.png")

    return images

# Example usage with dummy PDF bytes
# pdf_bytes = b'your_pdf_bytes_here'
# images = extract_images_from_pdf_bytes(pdf_bytes)
# This code will not extract embedded images directly but renders whole pages. 
# Extracting embedded images as separate entities would require accessing low-level page objects and is not directly supported in this simplified example.

