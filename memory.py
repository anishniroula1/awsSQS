import psutil
import threading
import time

# Function to monitor memory usage, prints memory every 5 seconds
def monitor_memory():
    while True:
        # Memory currently in use
        used_memory = psutil.virtual_memory().used / (1024 * 1024 * 1024)  # Convert bytes to GB
        print(f"Used Memory: {used_memory:.2f} GB")  # Formats the output to two decimal places
        time.sleep(5)  # Adjust the time interval as needed

# Start the memory monitoring in a separate thread
thread = threading.Thread(target=monitor_memory, daemon=True)
thread.start()

# Your OCR code here
# Replace the following line with your actual OCR code
time.sleep(60)  # Simulate long-running OCR process


def get_memory_limit_in_mb():
    """
    Returns the memory limit assigned to the container in megabytes,
    or None if not running in a container or limit is not set.
    """
    try:
        with open('/sys/fs/cgroup/memory/memory.limit_in_bytes', 'r') as file:
            # Convert from bytes to MB
            memory_limit_bytes = int(file.read().strip())
            memory_limit_mb = memory_limit_bytes / (1024 * 1024)
            return memory_limit_mb
    except Exception as e:
        print(f"An error occurred: {e}")
        return None