import json
import textwrap


# Step 1: Read the JSON file
with open('your_file.json', 'r') as file:
    data = json.load(file)

# Step 2: Sort the exchanges by the 'position' field
data['interview']['interviewData']['exchanges'] = sorted(
    data['interview']['interviewData']['exchanges'],
    key=lambda x: x['position']
)

# Step 3: Write the sorted data to a new JSON file
with open('sorted_file.json', 'w') as outfile:
    json.dump(data, outfile, indent=2)

print("The sorted data has been written to 'sorted_file.json'.")
