import pytest
from unittest.mock import patch, MagicMock
from PIL import Image
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
    image = Image.new("RGB", (200, 200), "white")

    # Mock OCR API behavior
    mock_api_instance = MagicMock()
    mock_tess_api.return_value.__enter__.return_value = mock_api_instance
    mock_api_instance.Recognize.return_value = None
    mock_api_instance.GetIterator.return_value.GetUTF8Text.return_value = "Mocked OCR Text"
    mock_api_instance.GetIterator.return_value.Confidence.return_value = 95

    text, conf = ocr_processor._OCRProcessor__pil_page_to_text(image)
    assert text == "Mocked OCR Text"
    assert conf == "0"  # Confidence > 85 maps to "0"


@patch("OCR.ImageProcessing.ImageProcessing.pdf_to_images")
@patch("tesserocr.PyTessBaseAPI")
def test_execute_ocr_process(mock_tess_api, mock_pdf_to_images):
    ocr_processor = OCRProcessor()

    # Mock PDF to images conversion
    mock_image = Image.new("RGB", (100, 100), "white")
    mock_pdf_to_images.return_value = [mock_image]  # Simulate one-page PDF

    # Mock OCR API behavior
    mock_api_instance = MagicMock()
    mock_tess_api.return_value.__enter__.return_value = mock_api_instance
    mock_api_instance.Recognize.return_value = None
    mock_api_instance.GetIterator.return_value.GetUTF8Text.return_value = "Mocked OCR Text"
    mock_api_instance.GetIterator.return_value.Confidence.return_value = 95

    # Run the function
    dummy_pdf_bytes = b"%PDF-1.4\n%%EOF"
    result = ocr_processor.execute_ocr_process(dummy_pdf_bytes)

    # Assertions
    assert isinstance(result, dict)
    assert result["text"] == "Mocked OCR Text"
    assert result["ocr_conf"] == "0"  # Confidence > 85 maps to "0"


if __name__ == "__main__":
    pytest.main()
