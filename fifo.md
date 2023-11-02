AWS Simple Queue Service (SQS) FIFO Queue Documentation
Amazon Simple Queue Service (SQS) offers a robust, secure, and highly scalable hosted queue that lets you integrate and decouple distributed software systems and components. Among its queue offerings, SQS provides a FIFO (First-In-First-Out) queue service that ensures a strict ordering of messages, aiding in situations where the order of operations and events is crucial.

Features of SQS FIFO Queues:
1. FIFO (First-In-First-Out) Delivery:
Messages are processed in the order they are sent and received, which is essential for scenarios like processing payment transactions or executing commands that have dependencies.
2. Exactly-Once Processing:
Ensures that a message is delivered once and remains available until a consumer processes and deletes it, which is critical in scenarios where duplicate messages could cause erroneous processing or create incorrect state in systems.
3. Transaction Rate:
Supports up to 300 transactions per second (TPS), or up to 3000 TPS with batching, meeting the needs of high-throughput systems.
4. Message Groups:
Allows the grouping of messages into ordered sets within a single queue. Messages within a group are always processed one by one, in a strict order.
5. Message Deduplication:
Provides a built-in way to prevent message duplication. Each message has a deduplication ID, and if a message with a particular deduplication ID is sent successfully, any subsequent messages with the same deduplication ID are accepted but not redelivered during a 5-minute deduplication interval.
6. Queue Naming Convention:
FIFO queue names must end with the .fifo suffix.
7. Producer and Consumer Support:
Supports one or more producers and consumers. Messages are stored in the order they were successfully received by SQS, and each message group can only be processed by one consumer at a time.
8. Limited AWS Service Support:
Not all AWS services support FIFO queues, like Auto Scaling Lifecycle Hooks, AWS IoT Rule Actions, AWS Lambda Dead-Letter Queues, and Amazon S3 Event Notifications.
9. Buffered Asynchronous Client Support:
The SQS Buffered Asynchronous Client currently does not support FIFO queues.
SQS Standard Queues vs SQS FIFO Queues:
Standard Queues:
At-Least-Once Delivery: Messages are delivered at least once, but duplicates can occur.
Ordering: Messages may be delivered in a different order than they were sent.
Higher Throughput: Typically higher throughput than FIFO queues.
FIFO Queues:
Exactly-Once Processing: Messages are delivered once, and duplicates are not tolerated.
Strict Ordering: Messages are delivered in the exact order in which they were sent.
Lower Throughput: Typically lower throughput than standard queues, but with the guarantee of order and single processing.