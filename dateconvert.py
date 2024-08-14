from datetime import datetime

def parse_datetime(date_time_str):
    # Define possible datetime formats
    formats = [
        "%Y-%m-%d %H:%M:%S.%f%z",       # with milliseconds and timezone
        "%Y-%m-%dT%H:%M:%S.%f%z",       # ISO format with milliseconds and timezone
        "%Y-%m-%d %H:%M:%S.%f",         # with milliseconds, no timezone
        "%Y-%m-%dT%H:%M:%S.%f",         # ISO format with milliseconds, no timezone
        "%Y-%m-%d %H:%M:%S%z",          # without milliseconds, with timezone
        "%Y-%m-%dT%H:%M:%S%z",          # ISO format without milliseconds, with timezone
        "%Y-%m-%d %H:%M:%S",            # without milliseconds, no timezone
        "%Y-%m-%dT%H:%M:%S"             # ISO format without milliseconds, no timezone
    ]
    
    # Try each format until one works
    for fmt in formats:
        try:
            return datetime.strptime(date_time_str, fmt)
        except ValueError:
            continue
    
    # If none of the formats worked
    raise ValueError(f"Date format for '{date_time_str}' not recognized")

# Example usage
date_time_str = "2023-12-21 23:09:39.365+00"
date_time_obj = parse_datetime(date_time_str)
print(date_time_obj)

# Convert back to your desired format
formatted_date_time_str = date_time_obj.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
print(formatted_date_time_str)

