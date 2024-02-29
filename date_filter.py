from datetime import datetime

# Example list of JSON objects
json_list = [
    {"id": 1, "status": "active", "created": "2024-02-20T12:00:00"},
    {"id": 2, "status": "active", "created": "2024-02-21T15:30:00"},
    {"id": 3, "status": "active", "created": "2024-02-22T10:45:00"}
]

# Convert the 'created' string to a datetime object and sort the list
json_list.sort(key=lambda x: datetime.strptime(x['created'], "%Y-%m-%dT%H:%M:%S"), reverse=True)

# The first element is the most recently created JSON object
most_recent_json = json_list[0]

print(most_recent_json)

"""

This repository hosts the code responsible for orchestrating the ingestion process of electronically filed cases from XYZ. It utilizes a State Machine to separate the business logic from the ingestion tasks, ensuring a flexible and scalable approach suitable not only for e-filed cases but for other applications as well. When a document's status changes in the PostgreSQL database, it triggers an AWS Lambda function. This function evaluates the document's new status and then routes a corresponding message to the appropriate Amazon SQS queue, ensuring that each document is processed in the correct manner based on its current state.
"""
