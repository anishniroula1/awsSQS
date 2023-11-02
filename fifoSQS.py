import boto3
from botocore.exceptions import ClientError

# Initialize a session using Amazon SQS
sqs = boto3.client('sqs')

def create_queue(queue_name):
    try:
        response = sqs.create_queue(
            QueueName=f'{queue_name}.fifo',  # Ensure the queue name ends with .fifo
            Attributes={'FifoQueue': 'true'}  # Specify this is a FIFO queue
        )
        print(f'Queue URL: {response["QueueUrl"]}')
        return response['QueueUrl']
    except ClientError as e:
        print(f'An error occurred: {e}')
        return None

def send_message(queue_url, message):
    try:
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=message,
            # MessageGroupId='1',  # You can change this as per your use case
            # MessageDeduplicationId=message,  # Optional, omit if ContentBasedDeduplication is enabled
            MessageAttributes={
                'Attribute1': {'StringValue': 'Value1', 'DataType': 'String'},
                'Attribute2': {'StringValue': 'Value2', 'DataType': 'String'},
            }
        )
        print(f'Message ID: {response["MessageId"]}')
    except ClientError as e:
        print(f'An error occurred: {e}')


def receive_messages(queue_url):
    try:
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=5,
            MessageAttributeNames=['All']  # Retrieve all message attributes
        )
        messages = response.get('Messages', [])
        return messages
    except ClientError as e:
        print(f'An error occurred: {e}')
        return None

def delete_messages(queue_url, messages):
    entries = [{'Id': msg['MessageId'], 'ReceiptHandle': msg['ReceiptHandle']} for msg in messages]
    try:
        response = sqs.delete_message_batch(QueueUrl=queue_url, Entries=entries)
        for result in response.get('Successful', []):
            print(f'Message {result["Id"]} deleted successfully')
    except ClientError as e:
        print(f'An error occurred: {e}')

def process_message(message):
    print(f'Processing message: {message["Body"]}')
    attributes = message.get('MessageAttributes', {})
    for name, value in attributes.items():
        print(f' - {name}: {value["StringValue"]}')

if __name__ == '__main__':
    queue_name = 'testFifo'
    queue_url = create_queue(queue_name)
    if queue_url:
        message = 'Hello, World!'
        # send_message(queue_url, message)
        while True:
            messages = receive_messages(queue_url)
            if messages:
                print(messages, 123)
                for message in messages:
                    process_message(message)
                delete_messages(queue_url, messages)

