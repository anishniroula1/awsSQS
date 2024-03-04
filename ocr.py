import cv2
import numpy as np
from pdf2image import convert_from_bytes
from PIL import Image
import spacy
import tesserocr
from tesserocr import PyTessBaseAPI, PSM, RIL
import fitz

class OCRProcessor:
    def __init__(self, ocr_threshold = 90):
        self.ocr_threshold = ocr_threshold

    # def pdf_to_images(self, pdf_bytes):
    #     try:
    #         # Converts PDF byte stream to a list of images
    #         images = convert_from_bytes(pdf_bytes)
    #         print(f"Successfully converted PDF to {len(images)} images.")
    #         return images
    #     except Exception as e:
    #         print(f"Error converting PDF to images: {e}")
    #         return []
        
    def pdf_to_images(self, pdf_bytes):
    images = []
    try:
        # Write PDF bytes to a temporary file
        with tempfile.NamedTemporaryFile(delete=True, suffix='.pdf') as temp_pdf:
            temp_pdf.write(pdf_bytes)
            temp_pdf.seek(0)  # Go to the start of the file

            # Determine the number of pages by converting the first page
            temp_images = convert_from_path(temp_pdf.name, first_page=0, last_page=0)
            num_pages = len(temp_images)  # Adjust based on actual page count if needed

            # Convert each page to an image one at a time
            for page_number in range(num_pages):
                page_images = convert_from_path(temp_pdf.name, first_page=page_number, last_page=page_number, dpi=150, thread_count=1)
                if page_images:  # Check if the list is not empty
                    images.append(page_images[0])

            print(f"Successfully converted PDF to {len(images)} images.")
            return images
    except Exception as e:
        print(f"Error converting PDF to images: {e}")
        return []

    @staticmethod
    def rotate_image(image, angle):
        try:
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            if -90 < angle < -45:
                angle += 90  # Adjusting angle for proper rotation

            two_d_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            cos = np.abs(two_d_matrix[0, 0])
            sin = np.abs(two_d_matrix[0, 1])

            new_w = int((h * sin) + (w * cos))
            new_h = int((h * cos) + (w * sin))

            two_d_matrix[0, 2] += (new_w // 2) - center[0]
            two_d_matrix[1, 2] += (new_h // 2) - center[1]

            rotated_image = cv2.warpAffine(image, two_d_matrix, (new_w, new_h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            return rotated_image
        except Exception as e:
            print(f"Error rotating image: {e}")
            return image  # Return original image if rotation fails

    def correct_image_alignment(self, image):
        try:
            open_cv_image = np.array(image)
            gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            coords = np.column_stack(np.where(thresh > 0))
            angle = cv2.minAreaRect(coords)[-1]

            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle

            corrected_image_pil = Image.fromarray(cv2.cvtColor(self.rotate_image(open_cv_image, angle), cv2.COLOR_BGR2RGB))
            print("Corrected image alignment.")
            return corrected_image_pil
        except Exception as e:
            print(f"Error correcting image alignment: {e}")
            return Image.fromarray(open_cv_image)  # Return original image if correction fails
        
    # def pil_page_to_text(self, page, return_confidence=False):
    #     """  converts a page with PIL format to text includes confidence scores in return_confidence
    #     param page: PIL.PpmImagePlugin.PpmImageFile
    #     sparam return_confidence: adds confidence score to returned result :return: OCRed text as string or two strings if return_confidence
    #     """
    #     with PyTessBaseAPI(psm=PSM.AUTO, path="/usr/share/tesseract-ocr/5/tessdata") as api:
    #     # set image as the current page
    #     # note: SetImage is inherited from tesserocr.PyTessBaseAPI
    #         api.SetImage(page)
    #         # Recognize the previously page
    #         # note: Recognize is inherited from tesserocr.PyTessBaseAPI
    #         is_text_recognized = api.Recognize()
    #         assert is_text_recognized is True
    #         try:
    #             text_words = [
    #                 w.GetUTF8Text(tesserocr.RIL.WORD)
    #                 for w in tesserocr.iterate_level(self.GetIterator(), tesserocr.RIL.WORD)]
    #         except Exception:
    #             if return_confidence:
    #                 return "", ""
    #             else:
    #                 return ""
    #         if return_confidence:
    #         # iterate at a SYMBOL level - not word level
    #         # such that the OCR confidence for each SYMBOL is returned
    #         # w. Confidence returns score from 0 to 100 which are thresholded and assigne
    #         # to 0 (good OCR) or 1 (bad OCR)
    #         # NOTE: this method skips blank spaces
    #             confidence_scores = [
    #                 "o" if w.Confidence(tesserocr.RIL.SYMBOL) >= self.ocr_threshold else "1" 
    #                 for w in tesserocr.iterate_level(api.GetIterator(), tesserocr.RIL.SYMBOL)
    #             ]
    #             # identify the skipped blank spaces via the word list, add a 0 in
    #             cumulative_word_len = 0
    #             for word in text_words[:-1]:
    #                 cumulative_word_len += len(word)
    #             # insert a 0 into list of OCR confidence scores where blank spots should be
    #                 confidence_scores.insert (cumulative_word_len, "0")
    #                 cumulative_word_len += 1

    #                 # join scores together as a single string
    #                 confidence_scores = "".join(confidence_scores)
    #         else:
    #             confidence_scores = None

    #         # remove set image from memory
    #         api.Clear()

    #         # join list of words together as one string and return with confider
    #         text_words = " ".join(text_words)
    #         if return_confidence:
    #             return text_words, confidence_scores 
    #         else:
    #             return text_words
        
    def pil_page_to_text(self, page, return_confidence=True):
        full_text = ""
        ocr_confidences = []

        try:
            with PyTessBaseAPI(psm=PSM.AUTO, path="/usr/share/tesseract-ocr/5/tessdata") as api:
                api.SetImage(page)
                api.Recognize()
                iter = api.GetIterator()
                level = RIL.WORD  # Iterate at word level

                while iter:
                    word = iter.GetUTF8Text(level)
                    conf = iter.Confidence(level)

                    if word and not word.isspace():  # Check if the word is not just space
                        # spacy_token = self.nlp(word.strip())
                        adjusted_conf = '0' if conf > 85 else '1'  # High confidence if any token is alpha
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
        try:
            images = self.pdf_to_images(pdf_bytes)
            combined_text = ""
            combined_ocr_confidences = ""

            for index, image in enumerate(images):
                print(f"Processing page {index + 1} of {len(images)}...")
                corrected_image = self.correct_image_alignment(image)
                full_text, ocr_confidences = self.pil_page_to_text(corrected_image, return_confidence=True)
                combined_text += full_text + " "  # Add space between text of different images
                if (index + 1) < len(images):
                    combined_ocr_confidences += ocr_confidences + '0'  # Add space in confidence string between pages
                else:
                    combined_ocr_confidences += ocr_confidences
            return {"text": combined_text.strip(), "ocr_conf": combined_ocr_confidences.strip()}
        except Exception as e:
            print(f"Error executing OCR process: {e}")
            return {"text": "", "ocr_conf": ""}

# Example usage
if __name__ == "__main__":
    try:
        with open("./test0.pdf", "rb") as file:
            print("Starting OCR process...")
            pdf_bytes = file.read()
            ocr_processor = OCRProcessor()
            ocr_data = ocr_processor.execute_ocr_process(pdf_bytes)
            print(ocr_data)
            print(f"Text length: {len(ocr_data['text'])}, OCR Confidence length: {len(ocr_data['ocr_conf'])}")
    except Exception as e:
        print(f"An error occurred while processing the file: {e}")




"""
tesserocr==2.6.2
spacy==3.7.4
numpy==1.26.4
pdf2image==1.17.0
Pillow==10.2.0
opencv-python-headless==4.9.0.80
"""