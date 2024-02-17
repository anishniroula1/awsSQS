import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
import tesserocr

class FileProcessor:
    def __init__(self, file_bytes, file_type):
        self.file_bytes = file_bytes
        self.file_type = file_type
    
    @staticmethod
    def deskew(image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.bitwise_not(gray)
        coords = np.column_stack(np.where(gray > 0))
        angle = cv2.minAreaRect(coords)[-1]
        
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

        return rotated

    @staticmethod
    def extract_text_from_image(image):
        image_pil = Image.fromarray(image)
        with tesserocr.PyTessBaseAPI() as api:
            api.SetImage(image_pil)
            api.Recognize()

            full_text = ""
            ocr_confidence_per_char = []

            iter_ = api.GetIterator()
            level = tesserocr.RIL.WORD
            while iter_:
                word = iter_.GetUTF8Text(level)  # Get the word text
                if word:  # If there's a word
                    conf_value = iter_.Confidence(level)
                    for char in (word + " "):
                        ocr_confidence_per_char.append("0" if conf_value >= 85 else "1")
                    full_text += word + " "
                if not iter_.Next(level):  # Move to the next word
                    break

            full_text = full_text.strip()
            ocr_confidence_str = ''.join(ocr_confidence_per_char)

            return full_text, ocr_confidence_str

    def process_image_from_bytes(self):
        nparr = np.frombuffer(self.file_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        preprocessed_image = self.deskew(image)
        text, ocr_confidence = self.extract_text_from_image(preprocessed_image)
        return {"text": text, "ocr_confidence": ocr_confidence}

    def process_pdf_from_bytes(self):
        doc = fitz.open("pdf", self.file_bytes)
        all_text = ""
        all_ocr_confidence = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap()
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
            if pix.n - 1:  # if not grayscale, convert to BGR
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            preprocessed_image = self.deskew(img)
            text, ocr_confidence = self.extract_text_from_image(preprocessed_image)
            all_text += text + " "
            all_ocr_confidence += ocr_confidence
        return {"text": all_text.strip(), "ocr_confidence": all_ocr_confidence}

    def extract_text(self):
        if self.file_type == 'pdf':
            return self.process_pdf_from_bytes()
        else:
            return self.process_image_from_bytes()
