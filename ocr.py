import os
import tempfile
import cv2
import numpy as np
from pdf2image import convert_from_bytes, convert_from_path
from PIL import Image
import spacy
import tesserocr
from tesserocr import PyTessBaseAPI, PSM, RIL
import fitz


class OCRProcessor:
    """
    This class is responsible for the Optical Character Recognition (OCR) processing of images.
    It includes functionality for correcting image alignment and converting images to text.
    """

    def __init__(self, ocr_threshold=90):
        self.ocr_threshold = ocr_threshold

    def pdf_to_images(self, pdf_bytes):
        """
        Converts a PDF file to a series of images, one for each page.

        Parameters:
            pdf_bytes (bytes): The PDF file content in bytes.

        Yields:
            PIL.Image: An image for each page of the PDF.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(pdf_bytes)
            temp_pdf.seek(0)
            temp_pdf.flush()
            os.fsync(temp_pdf.fileno())

            doc = fitz.open(temp_pdf.name)
            num_pages = doc.page_count
            doc.close()

            for page_number in range(1, num_pages + 1):
                page_images = convert_from_path(
                    temp_pdf.name,
                    first_page=page_number,
                    last_page=page_number,
                    dpi=150,
                    thread_count=1,
                )
                if page_images:
                    print(f"Yielding image for page {page_number}")
                    yield page_images[0]

            os.remove(temp_pdf.name)

    @staticmethod
    def rotate_image(image):
        """
        Rotates an image to correct its orientation based on the detected text orientation.

        Parameters:
            image (numpy.ndarray): The image to be rotated.

        Returns:
            numpy.ndarray: The rotated image.
        """
        try:
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)

            two_d_matrix = cv2.getRotationMatrix2D(center, 0, 1.0)
            cos = np.abs(two_d_matrix[0, 0])
            sin = np.abs(two_d_matrix[0, 1])

            new_w = int((h * sin) + (w * cos))
            new_h = int((h * cos) + (w * sin))

            two_d_matrix[0, 2] += (new_w // 2) - center[0]
            two_d_matrix[1, 2] += (new_h // 2) - center[1]

            rotated_image = cv2.warpAffine(
                image,
                two_d_matrix,
                (new_w, new_h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE,
            )
            return rotated_image
        except Exception as e:
            print(f"Error rotating image: {e}")
            return image  # Return original image if rotation fails

    def correct_image_alignment(self, image):
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
            with PyTessBaseAPI(
                psm=PSM.AUTO_OSD, path="/usr/share/tesseract-ocr/5/tessdata"
            ) as api:
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
                    corrected_image_pil = Image.fromarray(
                        self.rotate_image(open_cv_image)
                    )
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
            with PyTessBaseAPI(
                psm=PSM.AUTO_OSD, path="/usr/share/tesseract-ocr/5/tessdata"
            ) as api:
                api.SetImage(page)
                api.Recognize()
                iter = api.GetIterator()
                level = RIL.WORD  # Iterate at word level

                while iter:
                    word = iter.GetUTF8Text(level)
                    conf = iter.Confidence(level)

                    if (
                        word and not word.isspace()
                    ):  # Check if the word is not just space
                        adjusted_conf = "0" if conf > 85 else "1"
                        full_text += word + " "
                        ocr_confidences.extend([adjusted_conf] * len(word.strip()))
                    else:
                        full_text += " "  # Add space to the text
                        ocr_confidences.append("0")  # Space is always '0' confidence

                    if not iter.Next(level):
                        break

                # Clear the image from memory
                api.Clear()

                cleaned_text = full_text.strip()
                cleaned_confidences = "".join(ocr_confidences).strip()

                # Ensuring the final strings have the same length
                while len(cleaned_text) > len(cleaned_confidences):
                    cleaned_confidences += (
                        "0"  # Pad with '0' if text is longer than confidences
                    )
                return cleaned_text, cleaned_confidences
        except Exception as e:
            print(f"Error during OCR processing: {e}")
            return (
                full_text.strip(),
                "".join(ocr_confidences).strip(),
            )  # Return what was processed before error

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
            for index, image in enumerate(self.pdf_to_images(pdf_bytes)):
                print(f"Processing OCR for page {index + 1}...")
                corrected_image = self.correct_image_alignment(image)
                full_text, ocr_confidences = self.pil_page_to_text(
                    corrected_image, return_confidence=True
                )
                combined_text += full_text + " "
                combined_ocr_confidences += ocr_confidences

            return {
                "text": combined_text.strip(),
                "ocr_conf": combined_ocr_confidences.strip(),
            }
        except Exception as e:
            print(f"Error executing OCR process: {e}")
            return {"text": "", "ocr_conf": ""}


# Example usage
if __name__ == "__main__":
    try:
        with open("./test1.pdf", "rb") as file:
            print("Starting OCR process...")
            pdf_bytes = file.read()
            ocr_processor = OCRProcessor()
            ocr_data = ocr_processor.execute_ocr_process(pdf_bytes)
            print(ocr_data)
            print(
                f"Text length: {len(ocr_data['text'])}, OCR Confidence length: {len(ocr_data['ocr_conf'])}"
            )
    except Exception as e:
        print(f"An error occurred while processing the file: {e}")
