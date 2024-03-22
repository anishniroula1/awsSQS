import numpy as np
from PIL import Image
from OCR.ImageProcessing import ImageProcessing
import spacy
import tesserocr
from tesserocr import PyTessBaseAPI, PSM, RIL

class OCRProcessor:
    """
    This class is responsible for the Optical Character Recognition (OCR) processing of images.
    It includes functionality for correcting image alignment based on detected text orientation and converting images to text.
    """
    def __init__(self, ocr_threshold=90):
        self.ocr_threshold = ocr_threshold

    def correct_image_alignment(self, image, image_processor: ImageProcessing):
        """
        Corrects the alignment of the provided image based on its detected text orientation.

        Parameters:
            image (PIL.Image.Image): The image to be corrected.

        Returns:
            PIL.Image.Image: The corrected image.
        """
        try:
            open_cv_image = np.array(image)
            gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)

            # Using TesserOCR to find orientation
            with PyTessBaseAPI(psm=PSM.AUTO_OSD, path="/usr/share/tesseract-ocr/5/tessdata") as api:
                api.SetImage(Image.fromarray(gray))
                it = api.AnalyseLayout()
                orientation, direction, order, deskew_angle = it.Orientation()
                print("Orientation: {:d}".format(orientation))
                print("WritingDirection: {:d}".format(direction))
                print("TextlineOrder: {:d}".format(order))
                print("Deskew angle: {:.4f}".format(deskew_angle))
                angle = orientation
                if angle and angle != 0:
                    # Rotate image with updated angle
                    corrected_image_pil = Image.fromarray(image_processor.rotate_image(open_cv_image))
                else:
                    corrected_image_pil = Image.fromarray(open_cv_image)
            
            print("Corrected image alignment.")
            return corrected_image_pil
        except Exception as e:
            print(f"Error correcting image alignment: {e}")
            return Image.fromarray(open_cv_image)  # Return original if correction fails

        
    def pil_page_to_text(self, page, return_confidence=True):
        """
        Converts a page image to text using OCR, optionally returning confidence levels for the recognized text.

        Parameters:
            page (PIL.Image.Image): The page image to convert.
            return_confidence (bool): If true, returns confidence scores along with the text. Default is True.

        Returns:
            tuple: A tuple containing the OCR-converted text and a string representing confidence scores for each character.
        """
        full_text = ""
        ocr_confidences = []

        try:
            with PyTessBaseAPI(psm=PSM.AUTO_OSD, path="/usr/share/tesseract-ocr/5/tessdata") as api:
                api.SetImage(page)
                api.Recognize()
                iter = api.GetIterator()
                level = RIL.WORD  # Iterate at word level

                while iter:
                    word = iter.GetUTF8Text(level)
                    conf = iter.Confidence(level)

                    if word and not word.isspace():  # Check if the word is not just space
                        adjusted_conf = '0' if conf > 85 else '1' 
                        full_text += word + ' '
                        ocr_confidences.extend([adjusted_conf] * len(word.strip()))
                    else:
                        full_text += ' '  # Add space to the text
                        ocr_confidences.append('0')  # Space is always '0' confidence

                    if not iter.Next(level):
                        break

                # Clear the image from memory
                api.Clear()

                cleaned_text = full_text.strip()
                cleaned_confidences = ''.join(ocr_confidences).strip()

                # Ensuring the final strings have the same length
                while len(cleaned_text) > len(cleaned_confidences):
                    cleaned_confidences += '0'  # Pad with '0' if text is longer than confidences
                return cleaned_text, cleaned_confidences
        except Exception as e:
            print(f"Error during OCR processing: {e}")
            return full_text.strip(), ''.join(ocr_confidences).strip()  # Return what was processed before error

    def execute_ocr_process(self, pdf_bytes):
        """
        Executes the OCR process on a sequence of images, converting them to text.

        Parameters:
            images (iterator): An iterator yielding images for OCR processing.

        Returns:
            dict: A dictionary containing the combined text from all processed images and the corresponding OCR confidence scores.
        """
        try:
            combined_text = ""
            combined_ocr_confidences = ""
            image_processor = ImageProcessing()
            for index, image in enumerate(image_processor.pdf_to_images(pdf_bytes)):
                print(f"Processing OCR for page {index + 1}...")
                corrected_image = self.correct_image_alignment(image, image_processor)
                full_text, ocr_confidences = self.pil_page_to_text(corrected_image, return_confidence=True)
                combined_text += full_text + " "
                combined_ocr_confidences += ocr_confidences

            return {"text": combined_text.strip(), "ocr_conf": combined_ocr_confidences.strip()}
        except Exception as e:
            print(f"Error executing OCR process: {e}")
            return {"text": "", "ocr_conf": ""}
