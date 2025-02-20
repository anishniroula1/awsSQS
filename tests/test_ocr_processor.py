import pytest
import numpy as np
from PIL import Image
from OCR.OCRProcessor import OCRProcessor
from OCR.ImageProcessing import ImageProcessing


def test_correct_image_alignment():
    image_processor = ImageProcessing()
    ocr_processor = OCRProcessor()
    
    # Create a dummy image
    image = Image.new("RGB", (100, 100), color="white")

    # Test valid image correction
    corrected_image = ocr_processor._OCRProcessor__correct_image_alignment(image, image_processor)
    assert isinstance(corrected_image, Image.Image), "Corrected image should be a PIL Image"

    # Test error handling by passing an invalid image
    with pytest.raises(Exception):
        ocr_processor._OCRProcessor__correct_image_alignment(None, image_processor)


def test_pil_page_to_text():
    ocr_processor = OCRProcessor()

    # Create a dummy image with text
    image = Image.new("RGB", (200, 200), color="white")

    # Test OCR processing on a valid image
    text, conf = ocr_processor._OCRProcessor__pil_page_to_text(image)
    assert isinstance(text, str), "OCR text should be a string"
    assert isinstance(conf, str), "OCR confidence should be a string"
    
    # Test OCR processing on an empty image
    empty_image = Image.new("RGB", (100, 100), color="black")
    text, conf = ocr_processor._OCRProcessor__pil_page_to_text(empty_image)
    assert text == "", "OCR text should be empty for a blank image"
    assert conf == "", "OCR confidence should be empty for a blank image"


def test_execute_ocr_process():
    ocr_processor = OCRProcessor()
    image_processor = ImageProcessing()

    # Create a dummy PDF bytes
    dummy_pdf_bytes = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\n%%EOF"

    # Test valid OCR execution
    result = ocr_processor.execute_ocr_process(dummy_pdf_bytes)
    assert isinstance(result, dict), "OCR output should be a dictionary"
    assert "text" in result and "ocr_conf" in result, "OCR output should contain text and confidence"
    
    # Test OCR execution with invalid PDF bytes
    with pytest.raises(Exception):
        ocr_processor.execute_ocr_process(b"Invalid PDF")


if __name__ == "__main__":
    pytest.main()
