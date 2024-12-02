import os
import pandas as pd
import math

def save_file_names_to_excel_in_batches(folder_path, excel_file_path, batch_size=10):
    try:
        # List all files in the folder
        files_and_folders = os.listdir(folder_path)
        files = [file for file in files_and_folders if os.path.isfile(os.path.join(folder_path, file))]
        
        # Remove duplicates
        unique_files = list(set(files))
        total_files = len(unique_files)
        
        # Calculate files per batch
        files_per_batch = math.ceil(total_files / batch_size)
        
        # Prepare data with batch labels
        data = []
        for i, file in enumerate(unique_files):
            batch_number = (i // files_per_batch) + 1
            data.append({"Batch": f"Batch {batch_number}", "File Name": file})
        
        # Create a DataFrame
        df = pd.DataFrame(data)
        
        # Save the DataFrame to an Excel file
        df.to_excel(excel_file_path, index=False, sheet_name="File Names")
        
        print(f"File names have been saved to {excel_file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Replace these paths with your actual folder path and desired output file
folder_path = "your_folder_path_here"
excel_file_path = "output_file.xlsx"

save_file_names_to_excel_in_batches(folder_path, excel_file_path)
