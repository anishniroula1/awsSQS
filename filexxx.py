import datetime

# Sample data
files = [
    {"fileName": "file1.txt", "createdDate": "2024-03-25"},
    {"fileName": "file2.docx", "createdDate": "2024-05-15"},
    {"fileName": "file3.pdf", "createdDate": "2024-06-01"},
    {"fileName": "file4.txt", "createdDate": "2024-02-20"},
]

# Function to filter the list
def filter_files(files):
    filtered_files = []
    error_log = []

    for file in files:
        if not file['fileName'].endswith('.docx'):
            created_date = datetime.datetime.strptime(file['createdDate'], "%Y-%m-%d")
            if created_date > datetime.datetime(2024, 4, 30):
                error_log.append(f"Error: {file['fileName']} has a createdDate later than April 2024")
            else:
                filtered_files.append(file)
    
    return filtered_files, error_log

# Filter the files
filtered_files, error_log = filter_files(files)

# Output the results
print("Filtered Files:")
for file in filtered_files:
    print(file)

print("\nError Log:")
for error in error_log:
    print(error)
