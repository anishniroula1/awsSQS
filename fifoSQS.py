import boto3
from botocore.exceptions import ClientError

# Initialize a session using Amazon SQS
sqs = boto3.client("sqs")


def create_queue(queue_name):
    """
    The function creates a FIFO queue with the specified name and returns the URL of the created queue.

    :param queue_name: The `queue_name` parameter is the name of the queue that you want to create. It
    is a string value that you provide as an input to the `create_queue` function
    :return: the URL of the created queue.
    """
    try:
        response = sqs.create_queue(
            QueueName=f"{queue_name}.fifo",  # Ensure the queue name ends with .fifo
            Attributes={"FifoQueue": "true"},  # Specify this is a FIFO queue
        )
        print(f'Queue URL: {response["QueueUrl"]}')
        return response["QueueUrl"]
    except ClientError as e:
        print(f"An error occurred: {e}")
        return None


def send_message(queue_url, message):
    """
    The `send_message` function sends a message to an Amazon Simple Queue Service (SQS) queue with
    specified attributes.

    :param queue_url: The URL of the Amazon Simple Queue Service (SQS) queue to which you want to send
    the message
    :param message: The `message` parameter is the body of the message that you want to send to the
    queue. It can be a string or any other data type that can be serialized into a string
    """
    try:
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=message,
            MessageGroupId="1",  # You can change this as per your use case
            MessageAttributes={
                "Attribute1": {"StringValue": "Value1", "DataType": "String"},
                "Attribute2": {"StringValue": "Value2", "DataType": "String"},
            },
        )
        print(f'Message ID: {response["MessageId"]}')
    except ClientError as e:
        print(f"An error occurred: {e}")


def receive_messages(queue_url):
    """
    The function `receive_messages` retrieves up to 10 messages from an Amazon Simple Queue Service
    (SQS) queue specified by `queue_url` and returns them as a list.

    :param queue_url: The `queue_url` parameter is the URL of the Amazon Simple Queue Service (SQS)
    queue from which you want to receive messages. This URL uniquely identifies the queue and is
    provided by SQS when you create the queue
    :return: a list of messages received from the specified queue URL.
    """
    try:
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=5,
            MessageAttributeNames=["All"],  # Retrieve all message attributes
        )
        messages = response.get("Messages", [])
        return messages
    except ClientError as e:
        print(f"An error occurred: {e}")
        return None


def delete_messages(queue_url, messages):
    """
    The function `delete_messages` deletes a batch of messages from an Amazon Simple Queue Service (SQS)
    queue.

    :param queue_url: The `queue_url` parameter is the URL of the Amazon Simple Queue Service (SQS)
    queue from which you want to delete messages
    :param messages: The `messages` parameter is a list of messages that you want to delete from a
    queue. Each message in the list should be a dictionary containing the `MessageId` and
    `ReceiptHandle` attributes. The `MessageId` is a unique identifier for the message, and the
    `ReceiptHandle`
    """
    entries = [
        {"Id": msg["MessageId"], "ReceiptHandle": msg["ReceiptHandle"]}
        for msg in messages
    ]
    try:
        response = sqs.delete_message_batch(QueueUrl=queue_url, Entries=entries)
        for result in response.get("Successful", []):
            print(f'Message {result["Id"]} deleted successfully')
    except ClientError as e:
        print(f"An error occurred: {e}")


def process_message(message):
    """
    The function `process_message` prints the body of a message and its message attributes.

    :param message: The `message` parameter is a dictionary that represents a message. It has the
    following structure:
    """
    print(f'Processing message: {message["Body"]}')
    attributes = message.get("MessageAttributes", {})
    for name, value in attributes.items():
        print(f' - {name}: {value["StringValue"]}')


if __name__ == "__main__":
    queue_name = "testFifo"
    queue_url = create_queue(queue_name)
    if queue_url:
        message = "My baby!"
        send_message(queue_url, message)
        while True:
            messages = receive_messages(queue_url)
            if messages:
                print(messages, 123)
                for message in messages:
                    process_message(message)
                delete_messages(queue_url, messages)
