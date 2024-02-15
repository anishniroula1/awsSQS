import subprocess
import tempfile
import os

def repair_pdf_from_bytes_and_return_as_bytes(pdf_bytes):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_input_pdf:
            input_pdf_path = temp_input_pdf.name
            temp_input_pdf.write(pdf_bytes)
            temp_input_pdf.flush()
        
        output_pdf_path = f"{temp_input_pdf.name}_repaired.pdf"
        
        command = [
            "gs",
            "-o", output_pdf_path,
            "-sDEVICE=pdfwrite",
            "-dNOPAUSE",
            "-dDEBUG",
            input_pdf_path
        ]
        
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("Ghostscript output:", result.stdout)
        print("Ghostscript errors:", result.stderr)
        
        with open(output_pdf_path, 'rb') as repaired_pdf_file:
            return repaired_pdf_file.read()
    except subprocess.CalledProcessError as e:
        print(f"Ghostscript command failed: {e.stderr}")
        return None
    finally:
        # Cleanup temporary files
        if os.path.exists(input_pdf_path):
            os.remove(input_pdf_path)
        if os.path.exists(output_pdf_path):
            os.remove(output_pdf_path)
