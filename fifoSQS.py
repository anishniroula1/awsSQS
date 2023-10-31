import boto3
import json
from botocore.exceptions import ClientError

sqs = boto3.client('sqs')
queue_url = None

def create_queue(queue_name):
    global queue_url
    try:
        response = sqs.create_queue(
            QueueName=queue_name,
            Attributes={
                'FifoQueue': 'true',
                'ContentBasedDeduplication': 'true'
            }
        )
        queue_url = response['QueueUrl']
        print(f'Queue URL: {queue_url}')
        return queue_url
    except ClientError as e:
        print(f'An error occurred: {e}')
        return None

def send_message(message_body, message_group_id):
    if queue_url is None:
        print('Queue URL is None. Cannot send message.')
        return None

    try:
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message_body),
            MessageGroupId=message_group_id
        )
        return response
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def receive_messages():
    if queue_url is None:
        print('Queue URL is None. Cannot receive messages.')
        return None

    try:
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10  # Adjust as needed
        )
        return response.get('Messages', [])
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def delete_message(receipt_handle):
    if queue_url is None:
        print('Queue URL is None. Cannot delete message.')
        return None

    try:
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Usage
if __name__ == "__main__":
    create_queue('testFifo.fifo')
    
    if queue_url is not None:
        send_message({'hello': 'world'}, 'messageGroup1')
        messages = receive_messages()
        for message in messages:
            print(message['Body'])
            delete_message(message['ReceiptHandle'])
    else:
        print('Failed to create queue. Cannot proceed.')
