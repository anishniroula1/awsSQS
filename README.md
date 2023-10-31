# AWS SQS Message Handling in Python

This repository contains a Python script for interacting with Amazon Simple Queue Service (AWS SQS) using the `boto3` library.

## Script Overview

The script demonstrates basic operations with an SQS queue including creating a queue, sending a message to the queue, receiving messages from the queue, processing received messages, and deleting processed messages from the queue.

# Setup 
- Create a .env file
- add `AWS_ACCESS_KEY_ID` 
`AWS_SECRET_ACCESS_KEY` and other if you need for other permission.

``` txt
export AWS_ACCESS_KEY_ID=<KEY ID>
export AWS_SECRET_ACCESS_KEY=<AWS_SECRET_ACCESS_KEY>
```
- Make sure you source them ```source .env```

## Dependencies

- Python 3.x
- boto3
- botocore

Install dependencies with pip:

```bash
pip install boto3 botocore
```

## Functions
### create_queue(queue_name)
Creates a new SQS queue with the specified name.
- ```queue_name``` (str): The name of the queue to create.

### send_message(queue_url, message)
Sends a single message to the specified SQS queue.
- ```queue_url``` (str): The URL of the queue to which the message should be sent.
- ```message``` (str): The body of the message to send.

### receive_messages(queue_url)
Receives messages from the specified SQS queue.
- ```queue_url``` (str): The URL of the queue from which messages should be received.

### delete_messages(queue_url, messages)
Deletes a batch of messages from the specified SQS queue.
- ```queue_url``` (str): The URL of the queue from which messages should be deleted.
- ```messages``` (list): A list of message dictionaries to delete.

### process_message(message)
Processes a single message. This function is a placeholder and should be replaced with your own message processing logic.
- ```message``` (dict): A dictionary representing the message to process.

## Usage
- Ensure you have AWS credentials configured that have permissions to interact with AWS SQS.
- Update the queue_name variable in the ```__main__``` block to the name of your queue.
- Run the script




