from pdf2image import convert_from_bytes
import tempfile


def convert_pdf_bytestream_to_images(pdf_bytes):
    """
    Convert a PDF bytestream to images, one image per page.

    Args:
    - pdf_bytes (bytes): The bytestream of the PDF to be converted.

    Returns:
    - A list of images.
    """
    # Write the PDF bytestream to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as temp_pdf_file:
        temp_pdf_file.write(pdf_bytes)
        temp_pdf_file.seek(0)  # Go back to the start of the file

        # Convert the PDF file to images
        images = convert_from_bytes(temp_pdf_file.read(), dpi=200, fmt="jpeg")

    return images


# Example usage with placeholder for actual PDF bytes
pdf_bytes = b"your_pdf_bytes_here"  # Replace this with your actual PDF bytes
images = convert_pdf_bytestream_to_images(pdf_bytes)

# Optionally, save the images to files
for i, image in enumerate(images):
    image.save(f"page_{i}.jpeg", "JPEG")
