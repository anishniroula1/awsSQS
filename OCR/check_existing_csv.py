import pandas as pd

# Function to read and validate CSV files
def read_and_validate_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        if 'receipt_number' not in df.columns:
            raise ValueError(f"The file {file_path} does not contain a 'receipt_number' column.")
        return df
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

# Read the CSV files
file1_path = 'path/to/file1.csv'  # Replace with the actual path to file 1
file2_path = 'path/to/file2.csv'  # Replace with the actual path to file 2

df1 = read_and_validate_csv(file1_path)
df2 = read_and_validate_csv(file2_path)

if df1 is not None and df2 is not None:
    # Check for missing receipt numbers
    missing_receipts = df1[~df1['receipt_number'].isin(df2['receipt_number'])]['receipt_number']

    if missing_receipts.empty:
        print("All receipt numbers from file 1 are present in file 2.")
    else:
        print("The following receipt numbers from file 1 are not present in file 2:")
        print(missing_receipts.to_list())
else:
    print("One or both of the files could not be processed due to errors.")
