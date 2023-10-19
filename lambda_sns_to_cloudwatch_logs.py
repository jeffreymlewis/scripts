"""Write SNS message to the given Cloudwatch Logs group.

environment variables:
- CLOUDWATCH_LOG_GROUP_NAME: The Cloudwatch Logs group where messages should be
sent. A stream will be created in this log group matching the SNS Topic ARN
(invalid characters replaced with '_').
"""
import datetime
import os
import time

import boto3


class MissingEnvironmentVariableException(Exception):
  """Raised if a required environment variable is missing."""


def iso_to_epoch_ms(iso_format: str) -> int:
  """Takes a string in ISO format and returns seconds since epoch in ms
  presision.
  """
  dt = datetime.datetime.fromisoformat(iso_format)
  return int(dt.timestamp() * 1000)


def get_log_group_name() -> str:
  """Gets the Cloudwatch Log group name from an environment variable.
  """
  if not 'CLOUDWATCH_LOG_GROUP_NAME' in os.environ:
    raise MissingEnvironmentVariableException(
      'CLOUDWATCH_LOG_GROUP_NAME does not exist')

  return os.environ['CLOUDWATCH_LOG_GROUP_NAME']


# event: https://docs.aws.amazon.com/lambda/latest/dg/with-sns.html
# context: https://docs.aws.amazon.com/lambda/latest/dg/python-context.html
def lambda_handler(event, _) -> None:
  """Lambda calls this function to do the work.
  """
  logs = boto3.client('logs')

  log_group_name = get_log_group_name()

  for record in event['Records']:
    if not 'Message' in record['Sns']:
      print('SNS event contained no message, skipping')
      continue

    # Create Cloudwatch Log stream. Names cannot contain ':' or '*' and must be
    # 512 cahracters or less
    # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-logstream.html
    sns_topic_arn = (record['Sns']['TopicArn']
      .replace(':', '_').replace('*','_')[:512])
    try:
      logs.create_log_stream(logGroupName=log_group_name,
                             logStreamName=sns_topic_arn)
    except logs.exceptions.ResourceAlreadyExistsException:
      # log stream already exists, which is fine
      pass

    # Use SNS event timestamp if possible, else use current time
    if 'Timestamp' in record['Sns']:
      timestamp = iso_to_epoch_ms(record['Sns']['Timestamp'])
    else:
      timestamp = int(time.time() * 1000)

    # put log event in Cloudwatch Logs
    response = logs.put_log_events(
      logGroupName=log_group_name,
      logStreamName=sns_topic_arn,
      logEvents=[
        {
          'timestamp': timestamp,
          'message': record['Sns']['Message']
        }
      ]
    )

    if 'rejectedLogEventsInfo' in response:
      print(f'An error occurred: {response}')
