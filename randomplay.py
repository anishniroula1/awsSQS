import subprocess
import tempfile
import os

def repair_pdf_from_bytes_and_return_as_bytes(pdf_bytes):
    input_pdf_path = None
    output_pdf_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_input_pdf:
            input_pdf_path = temp_input_pdf.name
            temp_input_pdf.write(pdf_bytes)
            temp_input_pdf.flush()
        
        output_pdf_path = f"{temp_input_pdf.name}_repaired.pdf"

        command = [
            "gs",  # or "gswin64c" on Windows
            "-o", output_pdf_path,
            "-sDEVICE=pdfwrite",
            "-dPDFSETTINGS=/prepress",
            input_pdf_path
        ]

        subprocess.run(command, check=True, capture_output=True)
        
        with open(output_pdf_path, 'rb') as repaired_pdf_file:
            return repaired_pdf_file.read()
    except subprocess.CalledProcessError as e:
        print(f"Ghostscript command failed: {e.stderr.decode()}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if input_pdf_path and os.path.exists(input_pdf_path):
            os.remove(input_pdf_path)
        if output_pdf_path and os.path.exists(output_pdf_path):
            os.remove(output_pdf_path)
    return None
