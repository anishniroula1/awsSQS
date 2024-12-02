import os
import pandas as pd
import math

def save_file_names_in_nested_batches(folder_path, excel_file_path, batch_size=10):
    try:
        # List all files in the folder
        files_and_folders = os.listdir(folder_path)
        files = [file for file in files_and_folders if os.path.isfile(os.path.join(folder_path, file))]
        
        # Remove duplicates
        unique_files = list(set(files))
        
        # Split the files into batches
        batches = [unique_files[i:i + batch_size] for i in range(0, len(unique_files), batch_size)]
        
        # Create a DataFrame for the Excel file
        data = []
        for i, batch in enumerate(batches, start=1):
            data.append({"Batch": f"Batch {i}", "Files": str(batch)})
        
        df = pd.DataFrame(data)
        
        # Save the DataFrame to an Excel file
        df.to_excel(excel_file_path, index=False, sheet_name="File Batches")
        
        print(f"File batches have been saved to {excel_file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Replace these paths with your actual folder path and desired output file
folder_path = "your_folder_path_here"
excel_file_path = "output_file.xlsx"

save_file_names_in_nested_batches(folder_path, excel_file_path)
