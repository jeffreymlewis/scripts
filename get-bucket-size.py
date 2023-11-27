#!/usr/bin/env python3
#
# Return the size of all S3 buckets in a given AWS account.

import boto3
import botocore
import datetime


# An immutable list of S3 storage types, as referenced in CloudWatch Metrics by the `StorageType` dimension.
CLOUDWATCH_STORAGE_TYPESk = (
    "DeepArchiveObjectOverhead",
    "DeepArchiveS3ObjectOverhead",
    "DeepArchiveStorage",
    "GlacierInstantRetrievalStorage",
    "GlacierObjectOverhead",
    "GlacierS3ObjectOverhead",
    "GlacierStorage",
    "ReducedRedundancyStorage",
    "StandardIAStorage",
    "StandardStorage",
)


# TODO: This is incredibly slow due to all the different dimensions we need to pull to get a complete picture of S3
# bucket size. Would be great if we could return all AWS/S3 BucketSizeBytes metrics at once, and parse the JSON.
def get_bucket_size(bucket_name, region):
  """Return size of specified S3 bucket"""
  cloudwatch = boto3.client('cloudwatch', region_name=region)
  total_size = 0
  for storage_type in CLOUDWATCH_STORAGE_TYPES:
    response = cloudwatch.get_metric_statistics(
        Namespace='AWS/S3',
        MetricName='BucketSizeBytes',
        Dimensions=[
            {
                'Name': 'BucketName',
                'Value': bucket_name,
            },
            {
                'Name': 'StorageType',
                'Value': storage_type,
            }
        ],
        # For some reason, CloudWatch metrics are > 24 hours behind.
        StartTime=datetime.datetime.today() - datetime.timedelta(days=3),
        EndTime=datetime.datetime.today() - datetime.timedelta(days=2),
        Period=86400,
        Statistics=['Average'],
    )
    total_size += response['Datapoints'][0]['Average'] if response['Datapoints'] else 0
  return total_size


def list_all_buckets(s3_client):
  """Return list of all S3 buckets"""
  response = s3_client.list_buckets()
  return response['Buckets']


def get_bucket_region(s3_client, bucket_name):
  """Return region of specified bucket"""
  response = s3_client.get_bucket_location(Bucket=bucket_name)
  return response['LocationConstraint'] if response['LocationConstraint'] else 'us-east-1'


if __name__ == "__main__":
  s3_client = boto3.client('s3')
  buckets = {}
  for bucket in list_all_buckets(s3_client):
    bucket_name = bucket['Name']
    # skip restricted bucket
    if bucket_name == 'meetgroup-data':
      continue

    # get region
    try:
      region = get_bucket_region(s3_client, bucket_name)
    except botocore.exceptions.ClientError as err:
      # If the bucket doesn't exist, set size to -1 and continue. This way, our output still contains a complete list of buckets.
      if err.response['Error']['Code'] == 'NoSuchBucket':
        buckets[bucket_name] = -1
        continue
      else:
        raise err

    # get bucket size
    buckets[bucket_name] = get_bucket_size(bucket_name, region)

  # sort buckets by size and print with size in first column
  sorted_buckets = sorted([(v, k) for k, v in buckets.items()])
  for size, bucket in sorted_buckets:
    print('{}\t{}'.format(size, bucket))
