import boto3
import pandas as pd
import concurrent.futures
import time
import random
from botocore.exceptions import ClientError
from itertools import zip_longest

# Function to divide data into chunks
def chunk_data(data, size):
    return (data[pos:pos + size] for pos in range(0, len(data), size))

# Function to send a single batch with retry logic
def send_batch_with_retry(sqs_client, queue_url, batch, max_retries=5, base_delay=0.1):
    retries = 0
    while retries < max_retries:
        try:
            entries = [{'Id': str(index), 'MessageBody': record} for index, record in enumerate(batch)]
            response = sqs_client.send_message_batch(QueueUrl=queue_url, Entries=entries)
            return response
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['Throttling', 'ThrottlingException']:
                retries += 1
                delay = min(base_delay * 2 ** retries, 20) + (random.random() - 0.5)
                time.sleep(delay)
            else:
                raise e
    raise Exception("Max retries exceeded for batch send.")

def main(csv_file_path, sqs_queue_url):
    # Initialize the SQS client
    sqs = boto3.client('sqs', region_name='your-region-here')
    
    # Read the CSV file using pandas
    df = pd.read_csv(csv_file_path)
    
    # Assuming you want to send each row as a message; adjust as necessary
    records = df.to_json(orient='records', lines=True).splitlines()
    
    # Chunk the records into batches of 10
    record_batches = list(chunk_data(records, 10))
    
    # Use ThreadPoolExecutor to send batches in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
        futures = [executor.submit(send_batch_with_retry, sqs, sqs_queue_url, batch) for batch in record_batches]
        for future in concurrent.futures.as_completed(futures):
            try:
                response = future.result()
                # Handle successful response
                print(f"Batch sent successfully. {response}")
            except Exception as e:
                # Handle failure after max retries
                print(f"Failed to send batch after retries: {e}")

if __name__ == "__main__":
    csv_file_path = 'path/to/your/csvfile.csv'
    sqs_queue_url = 'your-sqs-queue-url-here'
    main(csv_file_path, sqs_queue_url)
