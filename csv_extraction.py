import csv
import re

# Helper function to extract class_id and class_group from text
def extract_class_info(raw_text):
    patterns = {
        'class_id': r'/api/class_id/([\w\-]+)',
        'second_class_id': r'/api/second_class_id/([\w\-]+)',
        'third_class_id': r'/api/third_class_id/([\w\-]+)',
    }

    for api_type, pattern in patterns.items():
        match = re.search(pattern, raw_text)
        if match:
            class_id = match.group(1)
            class_group = class_id.split('-')[0] if '-' in class_id else ''
            return api_type, class_id, class_group

    return None, None, None  # If no pattern matched

# Input and output files
input_file = 'input.csv'
output_class_id_file = 'class_id.csv'
output_other_classes_file = 'second_and_third_class_id.csv'

# Lists to collect rows for each file
class_id_rows = []
other_class_rows = []

# Read the input CSV and extract relevant info
with open(input_file, 'r', newline='', encoding='utf-8') as infile:
    reader = csv.DictReader(infile)

    for row in reader:
        raw_text = row.get('_raw', '')
        api_type, class_id, class_group = extract_class_info(raw_text)
        
        if class_id:
            output_row = {'class_id': class_id, 'class_group': class_group}
            if api_type == 'class_id':
                class_id_rows.append(output_row)
            elif api_type in ['second_class_id', 'third_class_id']:
                other_class_rows.append(output_row)

# Write class_id.csv
with open(output_class_id_file, 'w', newline='', encoding='utf-8') as outfile:
    writer = csv.DictWriter(outfile, fieldnames=['class_id', 'class_group'])
    writer.writeheader()
    writer.writerows(class_id_rows)

# Write second_and_third_class_id.csv
with open(output_other_classes_file, 'w', newline='', encoding='utf-8') as outfile:
    writer = csv.DictWriter(outfile, fieldnames=['class_id', 'class_group'])
    writer.writeheader()
    writer.writerows(other_class_rows)

print("Extraction and CSV writing complete.")
