from io import BytesIO
import pandas as pd

# Re-using the earlier JSON data for conversion
json_data = [
    {"Name": "John Doe", "Age": 28, "City": "New York"},
    {"Name": "Jane Doe", "Age": 34, "City": "Los Angeles"},
    {"Name": "Mike Tyson", "Age": 51, "City": "Las Vegas"},
    {"Name": "Sarah Connor", "Age": 45, "City": "San Francisco"},
    {"Name": "Tony Stark", "Age": 48, "City": "Malibu"},
    {"Name": "Peter Parker", "Age": 21, "City": "Queens"},
    {"Name": "Bruce Wayne", "Age": 35, "City": "Gotham"},
    {"Name": "Clark Kent", "Age": 36, "City": "Metropolis"},
    {"Name": "Diana Prince", "Age": 32, "City": "Themyscira"},
    {"Name": "Barry Allen", "Age": 28, "City": "Central City"},
]

# Convert JSON to a DataFrame
df_from_json = pd.DataFrame(json_data)

# Convert DataFrame to a CSV format and then to bytes
output = BytesIO()
df_from_json.to_csv(output, index=False)
output.seek(0)  # Go to the start of the BytesIO object

# Converting BytesIO object to bytes
csv_bytes = output.getvalue()
print(csv_bytes)

# Check the type to confirm conversion
type(csv_bytes), len(csv_bytes)
