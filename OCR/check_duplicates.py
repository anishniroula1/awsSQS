import pandas as pd

# Load the CSV file
df = pd.read_csv('your_file.csv')

# Group by student_id and document_category, then count the occurrences
category_counts = df.groupby(['student_id', 'document_category']).size().reset_index(name='count')

# Filter to find duplicates (where count > 1)
duplicates = category_counts[category_counts['count'] > 1]

# Display the duplicates
print(duplicates)
