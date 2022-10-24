#!/usr/bin/env python3

"""
List all AMIs.
List snapshots in AWS not assoicated with an AMI.
"""

import boto3
from pprint import pprint


def get_ec2_amis(region):
  """Return a list of AMIs in the given region."""
  ec2 = boto3.client('ec2', region_name=region)
  response = ec2.describe_images(Owners=['self'])
  return response['Images']

def get_ec2_snapshots(region, owner_ids):
  """Return list of snapshots in the given region, owned by the given owner."""
  ec2 = boto3.client('ec2', region_name=region)
  response = ec2.describe_snapshots(OwnerIds=owner_ids)
  return response['Snapshots']


if __name__ == '__main__':
  region = 'us-east-1'
  owners = ['444444444444']

  # Create dict of snapshots with key as SnapshotId for easy lookup
  snapshots = {}
  for snapshot in get_ec2_snapshots(region, owners):
    snapshot_id = snapshot['SnapshotId']
    snapshots[snapshot_id] = snapshot

  # Create a dictionary mapping SnapshotIds to ImageIds. This allows us to easily determine which snapshots are *not*
  # assoicated with an AMI.
  snapshot_to_ami = {}
  for snapshot_id in snapshots:
    snapshot_to_ami[snapshot_id] = []

  # Print a list of AMIs
  # Append AMI ImageId to the appropriate snapshot_to_ami mapping
  amis = get_ec2_amis(region)
  for ami in amis:
    device_size = 0
    for device in ami['BlockDeviceMappings']:
      if 'Ebs' in device:
        snapshot_id = device['Ebs']['SnapshotId']
        snapshot_to_ami[snapshot_id].append(ami['ImageId'])
        device_size += device['Ebs']['VolumeSize']
    print('{}\t{}\t{}'.format(device_size, ami['ImageId'], ami['Name']))

  # Print all snapshots which are *not* assoicated with an AMI
  for snapshot_id, amis in snapshot_to_ami.items():
    if not amis:
      print('{}\t{}\t{}'.format(snapshots[snapshot_id]['VolumeSize'], snapshots[snapshot_id]['SnapshotId'], snapshots[snapshot_id]['Description']))

