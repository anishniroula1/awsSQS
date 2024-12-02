import os
import pandas as pd

def save_file_names_to_excel(folder_path, excel_file_path):
    try:
        # List all files and folders in the given directory
        files_and_folders = os.listdir(folder_path)
        
        # Filter to get only files
        files = [file for file in files_and_folders if os.path.isfile(os.path.join(folder_path, file))]
        
        # Create a pandas DataFrame with the file names
        df = pd.DataFrame({'File Name': files})
        
        # Save the DataFrame to an Excel file
        df.to_excel(excel_file_path, index=False)
        
        print(f"File names have been saved to {excel_file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Replace 'your_folder_path_here' with the path to the folder you want to read
folder_path = "your_folder_path_here"
# Replace 'output_file.xlsx' with the desired output Excel file name
excel_file_path = "output_file.xlsx"

save_file_names_to_excel(folder_path, excel_file_path)
