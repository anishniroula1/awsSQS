from datetime import datetime

# Java LocalDateTime string
date_time_str = "2023-12-21 23:09:39.365+00"

# Adjust the timezone format to include the colon
if date_time_str.endswith('+00'):
    date_time_str = date_time_str[:-3] + '+00:00'
elif date_time_str.endswith('-00'):
    date_time_str = date_time_str[:-3] + '-00:00'

# Replace the space with 'T' to match the desired format
date_time_str = date_time_str.replace(' ', 'T')

# Parse the adjusted string into a datetime object
date_time_obj = datetime.strptime(date_time_str, "%Y-%m-%dT%H:%M:%S.%f%z")

# Convert the datetime object back to a string in the desired format
formatted_date_time_str = date_time_obj.strftime("%Y-%m-%dT%H:%M:%S.%f%z")

# Output the result
print(formatted_date_time_str)
