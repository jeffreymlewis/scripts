"""Write SNS message to the given Cloudwatch Logs group.

environment variables:
- CLOUDWATCH_LOG_GROUP_NAME
"""
import datetime
import os
import time

import boto3


class MissingEnvironmentVariableException(Exception):
    """Raised if a required environment variable is missing."""


def lambda_handler(event, context):
    """Lambda calls this function to do the work.
    """
    if 'CLOUDWATCH_LOG_GROUP_NAME' in os.environ:
        log_group_name = os.environ['CLOUDWATCH_LOG_GROUP_NAME']
    else:
        raise MissingEnvironmentVariableException("CLOUDWATCH_LOG_GROUP_NAME does not exist")

    logs = boto3.client('logs')

    # https://docs.aws.amazon.com/lambda/latest/dg/with-sns.html
    for record in event['Records']:
        if not 'Message' in record['Sns']:
            print("SNS event contained no message")
            continue

	    # Create Cloudwatch Log stream. Names cannot contain ':' or '*' and must be 512 cahracters
        # or less
        # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-logstream.html
        sns_topic_arn = record['Sns']['TopicArn'].replace(':', '_').replace('*','_')[:512]
        try:
            logs.create_log_stream(logGroupName=log_group_name, logStreamName=sns_topic_arn)
        except logs.exceptions.ResourceAlreadyExistsException:
            # log stream already exists, which is fine
            pass

        # Use SNS event timestamp if possible
        if 'Timestamp' in record['Sns']:
            timestamp = datetime.datetime.fromisoformat(record['Sns']['Timestamp']).timestamp()
        else:
            print("SNS event contained no timestamp, using current time")
            timestamp = time.time()

        # convert to milliseconds
        timestamp_ms = int(timestamp * 1000)

        # put log event in Cloudwatch Logs
        response = logs.put_log_events(
            logGroupName=log_group_name,
            logStreamName=sns_topic_arn,
            logEvents=[
                {
                    'timestamp': timestamp_ms,
                    'message': record['Sns']['Message']
                }
            ]
        )

        if 'rejectedLogEventsInfo' in response:
            print(f"An error occurred: {response}")
