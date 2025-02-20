import os
import tempfile
import cv2
import numpy as np
from pdf2image import convert_from_path
from PIL import Image
from PyPdf2 import PdfReader
import gc


class ImageProcessing:
    """
    This class handles operations related to image manipulation, including converting
    PDF pages to images and rotating images to correct their orientation.
    """

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

            try:
                doc = PdfReader(temp_pdf.name)
                pages = doc.pages
                num_pages = len(pages)

                for page_number in range(1, num_pages + 1):
                    page = pages[page_number - 1]
                    yield self.__convert_page(temp_pdf.name, page_number, page)
            except Exception as e:
                page_number = 1
                while True:
                    try:
                        page_images = convert_from_path(temp_pdf.name, first_page=page_number, last_page=page_number)
                        if not page_images:
                            break

                        image = page_images[0]
                        if image.height > 3600 or image.width > 2700:
                            yield image.resize((2200, 1700))
                        else:
                            yield image

                        page_number += 1
                        gc.collect()
                    except Exception as e:
                        raise Exception

            os.remove(temp_pdf.name)

    @staticmethod
    def __convert_page(pdf_path, page_number, page):
        doc_height = int(page.mediabox.height)
        doc_width = int(page.mediabox.width)

        if doc_height > 3600 or doc_width > 2700:
            page_images = convert_from_path(pdf_path, first_page=page_number, last_page=page_number,
                                            size=(2200, 1700))
        else:
            page_images = convert_from_path(pdf_path, first_page=page_number, last_page=page_number)

        if page_images:
            return page_images[0]


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
