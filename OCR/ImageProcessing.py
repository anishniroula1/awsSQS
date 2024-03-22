import os
import tempfile
import cv2
import numpy as np
from pdf2image import convert_from_bytes, convert_from_path
from PIL import Image
import fitz

class ImageProcessing:
    """
    This class handles operations related to image manipulation, including converting
    PDF pages to images and rotating images to correct their orientation.
    """
    @staticmethod
    def pdf_to_images(pdf_bytes):
        """
        Converts a PDF file to a series of images, one for each page.

        Parameters:
            pdf_bytes (bytes): The PDF file content in bytes.

        Yields:
            PIL.Image: An image for each page of the PDF.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
            temp_pdf.write(pdf_bytes)
            temp_pdf.seek(0)
            temp_pdf.flush()
            os.fsync(temp_pdf.fileno())

            doc = fitz.open(temp_pdf.name)
            num_pages = doc.page_count
            doc.close()

            for page_number in range(1, num_pages + 1):
                page_images = convert_from_path(temp_pdf.name, first_page=page_number, last_page=page_number, dpi=150, thread_count=1)
                if page_images:
                    print(f"Yielding image for page {page_number}")
                    yield page_images[0]

            os.remove(temp_pdf.name)

    @staticmethod
    def rotate_image(image, angle):
        """
        Rotates an image to correct its orientation based on a given angle.

        Parameters:
            image (numpy.ndarray): The image to be rotated.
            angle (float): The angle to rotate the image by.

        Returns:
            numpy.ndarray: The rotated image.
        """
        try:
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)

            two_d_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)  # Use the angle
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
