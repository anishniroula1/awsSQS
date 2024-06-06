import pandas as pd

# Read the SSV files
file1 = pd.read_csv("file1.ssv", sep=" ")
file2 = pd.read_csv("file2.ssv", sep=" ")

# Assuming the column containing receipt numbers is named 'receipt_number'
# Adjust the column name if it's different in your files
receipt_numbers_file1 = file1["receipt_number"]
receipt_numbers_file2 = file2["receipt_number"]

# Find receipt numbers in file1 that are not in file2
not_in_file2 = receipt_numbers_file1[~receipt_numbers_file1.isin(receipt_numbers_file2)]

# Convert the result to a list
not_in_file2_list = not_in_file2.tolist()

# Output the list
print(not_in_file2_list)
