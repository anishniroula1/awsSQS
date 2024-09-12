from datetime import datetime

def format_java_date_time(local_date_time: str):
    # Adjust the timezone format to include the colon
    if local_date_time.endswith("+00"):
        local_date_time = local_date_time[:-3] + "+00:00"
    elif local_date_time.endswith("-00"):
        local_date_time = local_date_time[:-3] + "-00:00"
    
    # Replace the space with 'T' to match the desired format
    local_date_time = local_date_time.replace(" ", "T")
    
    # Try parsing with milliseconds if present, otherwise parse without them
    try:
        # If there are milliseconds
        date_time_obj = datetime.strptime(local_date_time, "%Y-%m-%dT%H:%M:%S.%f%z")
    except ValueError:
        # If there are no milliseconds
        date_time_obj = datetime.strptime(local_date_time, "%Y-%m-%dT%H:%M:%S%z")
    
    # Convert the datetime object back to a string in the desired format
    formatted_date_time_str = date_time_obj.strftime("%Y-%m-%dT%H:%M:%S.%f%z")[:-2] + ":00"

    return formatted_date_time_str

# Test with both y and z
y = '2023-12-21 23:09:39.365+00'
z = '2024-09-12 00:31:39+00'

# Output for both cases
x = format_java_date_time(y)
print(x)
