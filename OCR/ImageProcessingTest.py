import pytest
from PIL import Image
from your_module import ImageProcessing  # Adjust this import based on your project structure.
import numpy as np
import tempfile
import os

# Fixture for generating temporary PDF file
@pytest.fixture
def create_pdf():
    content = "This is a sample PDF for testing."
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tf:
        # Use a PDF generation library to create a PDF or copy a predefined one
        # Here you would put code to generate a PDF into tf.name
        yield tf.name  # This will be used as the PDF path
        os.remove(tf.name)  # Cleanup after test

@pytest.fixture
def sample_image_bytes():
    # Create a sample image for rotation tests
    image = Image.new('RGB', (100, 100), color = 'red')
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tf:
        image.save(tf.name)
        tf.seek(0)
        yield tf.read()  # Provide image bytes
        os.remove(tf.name)  # Cleanup

def test_pdf_to_images(create_pdf):
    images = list(ImageProcessing.pdf_to_images(open(create_pdf, 'rb').read()))
    assert len(images) > 0, "No images generated from PDF"
    assert all(isinstance(img, Image.Image) for img in images), "Not all outputs are PIL images"

def test_rotate_image():
    original_image = np.zeros((100, 100, 3), dtype=np.uint8)
    original_image[20:80, 20:80] = 255  # Create a white square in the middle

    rotated_image = ImageProcessing.rotate_image(original_image, 45)  # Rotate 45 degrees

    assert rotated_image.shape[0] != original_image.shape[0], "Image height should change after rotation"
    assert rotated_image.shape[1] != original_image.shape[1], "Image width should change after rotation"

    # You might want to check if the white square is now rotated
    # This would involve more complex image processing checks.

def test_pdf_to_images_no_content():
    # Test how the method handles an empty or incorrect PDF
    empty_pdf_bytes = b''  # Represents an empty file, in reality, you might have corrupted PDF content here
    images = list(ImageProcessing.pdf_to_images(empty_pdf_bytes))
    assert len(images) == 0, "Should not generate images from empty or invalid PDF content"
