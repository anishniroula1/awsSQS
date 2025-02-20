import pytest
from unittest.mock import patch, MagicMock
from PIL import Image, ImageDraw
from OCR.OCRProcessor import OCRProcessor
from OCR.ImageProcessing import ImageProcessing


@patch("tesserocr.PyTessBaseAPI")
def test_correct_image_alignment(mock_tess_api):
    image_processor = ImageProcessing()
    ocr_processor = OCRProcessor()
    image = Image.new("RGB", (100, 100), "white")

    # Mock OCR API response
    mock_api_instance = MagicMock()
    mock_tess_api.return_value.__enter__.return_value = mock_api_instance
    mock_api_instance.AnalyseLayout.return_value.Orientation.return_value = (0, 0, 0, 0)

    corrected_image = ocr_processor._OCRProcessor__correct_image_alignment(image, image_processor)
    assert isinstance(corrected_image, Image.Image)


@patch("tesserocr.PyTessBaseAPI")
def test_pil_page_to_text(mock_tess_api):
    ocr_processor = OCRProcessor()

    # Create an image with text for OCR
    image = Image.new("RGB", (200, 100), "white")
    draw = ImageDraw.Draw(image)
    draw.text((10, 40), "Mocked OCR Text", fill="black")  # Add text to the image

    # Mock OCR API behavior
    mock_api_instance = MagicMock()
    mock_tess_api.return_value.__enter__.return_value = mock_api_instance
    mock_tess_iter = MagicMock()
    
    # Ensure GetIterator() returns a valid mock
    mock_api_instance.GetIterator.return_value = mock_tess_iter
    
    # Simulate OCR text retrieval
    mock_tess_iter.GetUTF8Text.return_value = "Mocked OCR Text"
    mock_tess_iter.Confidence.return_value = 95
    mock_tess_iter.Next.side_effect = [True, False]  # Simulate iterating once then stopping

    # Run OCR function
    text, conf = ocr_processor._OCRProcessor__pil_page_to_text(image)

    # Assertions
    assert text.strip() == "Mocked OCR Text", f"Expected 'Mocked OCR Text' but got '{text}'"
    assert conf == "0" * len("Mocked OCR Text".replace(" ", "")), f"Expected confidence mapping but got '{conf}'"


@patch("OCR.ImageProcessing.ImageProcessing.pdf_to_images")
@patch("tesserocr.PyTessBaseAPI")
def test_execute_ocr_process(mock_tess_api, mock_pdf_to_images):
    ocr_processor = OCRProcessor()

    # Mock PDF to images conversion
    image = Image.new("RGB", (200, 100), "white")
    draw = ImageDraw.Draw(image)
    draw.text((10, 40), "Mocked OCR Text", fill="black")  # Add text to the image
    mock_pdf_to_images.return_value = [image]  # Simulate one-page PDF

    # Mock OCR API behavior
    mock_api_instance = MagicMock()
    mock_tess_api.return_value.__enter__.return_value = mock_api_instance
    mock_tess_iter = MagicMock()
    mock_api_instance.GetIterator.return_value = mock_tess_iter
    
    # Simulate OCR text retrieval
    mock_tess_iter.GetUTF8Text.return_value = "Mocked OCR Text"
    mock_tess_iter.Confidence.return_value = 95
    mock_tess_iter.Next.side_effect = [True, False]  # Simulate one iteration

    # Run OCR function
    dummy_pdf_bytes = b"%PDF-1.4\n%%EOF"
    result = ocr_processor.execute_ocr_process(dummy_pdf_bytes)

    # Assertions
    assert isinstance(result, dict)
    assert result["text"] == "Mocked OCR Text", f"Expected 'Mocked OCR Text' but got '{result['text']}'"
    assert result["ocr_conf"] == "0" * len("Mocked OCR Text".replace(" ", "")), f"Expected confidence mapping but got '{result['ocr_conf']}'"


if __name__ == "__main__":
    pytest.main()
