#!/usr/bin/env python3
"""Print summary of all EC2 instances along with their total EBS disk size allocation. Indented under each EC2
instance, print each EBS volume including size and type."""

import boto3
from pprint import pprint


def get_ec2_reservations(region):
  """Return dictionary of EC2 instances from the given region."""
  ec2 = boto3.client('ec2', region_name=region)
  response = ec2.describe_instances()
  return response['Reservations']


def get_ebs_volumes(region):
  """Return a dictionary of all AWS EBS volumes in the given region"""
  ec2 = boto3.client('ec2', region_name=region)
  response = ec2.describe_volumes()
  return response['Volumes']


if __name__ == "__main__":
  region = 'us-east-1'

  # Create dictionary of volumes for easy lookup by VolumeId
  volumes = {}
  for volume in get_ebs_volumes(region=region):
    volumes[volume['VolumeId']] = volume

  # Print instances including all volume information
  for reservation in get_ec2_reservations(region=region):
    for instance in reservation['Instances']:
      # add up all disk sizes regardless of type
      total_ebs_size = 0
      for device in instance['BlockDeviceMappings']:
        if 'Ebs' in device:
          volume_id = device['Ebs']['VolumeId']
          total_ebs_size += volumes[volume_id]['Size']

      # print summery of total EBS size along with instanceId and 'Name'
      print('{}\t{}\t{}'.format(total_ebs_size, instance['InstanceId'], [tag['Value'] for tag in instance['Tags'] if tag['Key'] == 'Name']))
      # list all EBS volmes for this instance
      for device in instance['BlockDeviceMappings']:
        if 'Ebs' in device:
          volume_id = device['Ebs']['VolumeId']
          print('\t{}\t{}\t{}'.format(volume_id, volumes[volume_id]['Size'], volumes[volume_id]['VolumeType']))
      
