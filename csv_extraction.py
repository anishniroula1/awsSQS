import csv
import re
import os
from collections import defaultdict

# Function to extract class_id and class_group
def extract_class_info(raw_text):
    match = re.search(r'/api/class_id_[A-Z\-]+/([\w\-]+)/student', raw_text)
    if not match:
        return None, None
    class_id = match.group(1)
    
    # Check if it has a prefix (e.g., DE-123)
    if '-' in class_id:
        prefix = class_id.split('-')[0]
        return class_id, prefix
    else:
        return class_id, None

input_file = 'input.csv'
output_all_file = 'all_classes.csv'
class_group_files = defaultdict(list)

with open(input_file, 'r', newline='', encoding='utf-8') as infile:
    reader = csv.DictReader(infile)
    output_rows = []
    
    for row in reader:
        raw_text = row.get('_raw', '')
        class_id, class_group = extract_class_info(raw_text)
        if class_id:
            output_rows.append({'class_id': class_id, 'class_group': class_group if class_group else ''})
            if class_group:
                class_group_files[class_group].append({'class_id': class_id})

# Write master output file
with open(output_all_file, 'w', newline='', encoding='utf-8') as outfile:
    writer = csv.DictWriter(outfile, fieldnames=['class_id', 'class_group'])
    writer.writeheader()
    writer.writerows(output_rows)

# Write separate files for each class_group
for group, rows in class_group_files.items():
    filename = f'class_group_{group}.csv'
    with open(filename, 'w', newline='', encoding='utf-8') as group_file:
        writer = csv.DictWriter(group_file, fieldnames=['class_id'])
        writer.writeheader()
        writer.writerows(rows)

print("Extraction completed.")
