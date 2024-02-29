import io
from pdf2image import convert_from_bytes
import cv2
import numpy as np
from PIL import Image
import tesserocr
from tesserocr import PyTessBaseAPI, RIL, PSM
import spacy

class OCRProcessor:
    def __init__(self):
        # Load spaCy model for post-processing
        self.nlp = spacy.load("en_core_web_sm")

    def pdf_to_images(self, pdf_bytes):
        """Converts PDF byte stream to a list of images."""
        return convert_from_bytes(pdf_bytes)

    def correct_image_alignment(self, image):
        """Corrects the alignment of the given image using OpenCV."""
        open_cv_image = np.array(image)
        gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        coords = np.column_stack(np.where(thresh > 0))
        angle = cv2.minAreaRect(coords)[-1]
        
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        (h, w) = open_cv_image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        corrected_image = cv2.warpAffine(open_cv_image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        corrected_image_pil = Image.fromarray(cv2.cvtColor(corrected_image, cv2.COLOR_BGR2RGB))
        return corrected_image_pil

    def ocr_and_adjust_confidence(self, image):
        """Performs OCR on the given image and adjusts confidence using spaCy."""
        full_text = ""
        text_confidences = []

        with PyTessBaseAPI(psm=PSM.AUTO) as api:
            api.SetImage(image)
            api.Recognize()
            ri = api.GetIterator()
            level = RIL.WORD

            for r in tesserocr.iterate_level(ri, level):
                word = r.GetUTF8Text(level)
                conf = r.Confidence(level)
                full_text += word + " "
                text_confidences.append((word, conf))

        doc = self.nlp(full_text.strip())
        adjusted_confidences = []

        for token in doc:
            adjusted_conf = 0 if token.is_alpha and not token.is_stop else 1
            adjusted_confidences.append((token.text, adjusted_conf))

        return full_text.strip(), adjusted_confidences

    def execute_ocr_process(self, pdf_bytes):
        """Executes the entire OCR process on the given PDF byte stream."""
        images = self.pdf_to_images(pdf_bytes)
        all_texts_and_confidences = []

        for image in images:
            corrected_image = self.correct_image_alignment(image)
            full_text, adjusted_confidences = self.ocr_and_adjust_confidence(corrected_image)
            all_texts_and_confidences.append((full_text, adjusted_confidences))

        return all_texts_and_confidences


with open('./test1.pdf', 'rb') as file:
    print (file.read())