import subprocess
import tempfile
import os

def convert_docx_bytes_to_pdf_bytes(docx_bytes):
    with tempfile.TemporaryDirectory() as tmpdir:
        # Step 1: Save the DOCX byte stream to a temporary file
        input_docx_path = os.path.join(tmpdir, 'input.docx')
        with open(input_docx_path, 'wb') as docx_file:
            docx_file.write(docx_bytes)
        
        # Step 2: Convert the DOCX file to PDF using LibreOffice
        output_pdf_path = os.path.join(tmpdir, 'output.pdf')
        command = [
            'libreoffice',
            '--headless',  # Run in headless mode (without GUI)
            '--convert-to', 'pdf',  # Specify the output format
            '--outdir', tmpdir,  # Specify the output directory
            input_docx_path  # Input file path
        ]

        subprocess.run(command, check=True)
        
        # Step 3: Read the PDF file back into a byte stream
        with open(output_pdf_path, 'rb') as pdf_file:
            pdf_bytes = pdf_file.read()
        
        # Return the PDF byte stream
        return pdf_bytes
    
# Example usage:
if __name__ == "__main__":
    with open('example.docx', 'rb') as file:
        docx_bytes = file.read()

    try:
        pdf_bytes = convert_docx_bytes_to_pdf_bytes(docx_bytes)
        # Now you can save or use the pdf_bytes as needed
        with open('output_converted.pdf', 'wb') as file:
            file.write(pdf_bytes)
    except Exception as e:
        print(f"An error occurred: {e}")
