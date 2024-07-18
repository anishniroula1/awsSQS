from datetime import datetime

# Sample data
records = [
    {"fileName": "document1.docx", "createdDate": "2024-03-27T12:42:15.072+00:00"},
    {"fileName": "document2.pdf", "createdDate": "2024-05-01T12:42:15.072+00:00"},
    {"fileName": "document3.txt", "createdDate": "2024-02-15T12:42:15.072+00:00"},
    {"fileName": "document4.docx", "createdDate": "2024-04-10T12:42:15.072+00:00"}
]

# Function to filter records
def filter_records(records):
    filtered_records = []
    error_logs = []

    for record in records:
        file_name = record["fileName"]
        created_date = record["createdDate"]

        # Check if the file name does not end with .docx
        if not file_name.endswith(".docx"):
            filtered_records.append(record)

        # Parse the created date and check if it is later than April 2024
        date_format = "%Y-%m-%dT%H:%M:%S.%f%z"
        created_date_parsed = datetime.strptime(created_date, date_format)
        april_2024 = datetime(2024, 4, 30, 23, 59, 59, tzinfo=created_date_parsed.tzinfo)

        if created_date_parsed > april_2024:
            error_logs.append(f"Error: {file_name} has a created date later than April 2024.")

    return filtered_records, error_logs

# Filter the records
filtered_records, error_logs = filter_records(records)

# Print filtered records
print("Filtered Records:")
for record in filtered_records:
    print(record)

# Print error logs
print("\nError Logs:")
for error in error_logs:
    print(error)
