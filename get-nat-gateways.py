#!/usr/bin/env python3

import boto3


def get_subnets(region):
  """Return a list of subnets in the given region."""
  ec2 = boto3.client('ec2', region_name=region)
  response = ec2.describe_subnets()
  return response['Subnets']


def get_nat_gateways(region):
  """Return a list of NAT Gateways in the given region."""
  ec2 = boto3.client('ec2', region_name=region)
  response = ec2.describe_nat_gateways()
  return response['NatGateways']


def get_vpcs(region):
  """Return a list of VPCs in the given region."""
  ec2 = boto3.client('ec2', region_name=region)
  response = ec2.describe_vpcs()
  return response['Vpcs']


if __name__ == '__main__':
  region = 'us-east-1'

  # Get all VPCs, so we can pull the 'Name' tag if it exists
  vpcs = {}
  for vpc in get_vpcs(region):
    vpc_id = vpc['VpcId']
    vpcs[vpc_id] = vpc

  # Get all subnets, so we can pull the 'Name' tag if it exists
  subnets = {}
  for subnet in get_subnets(region):
    subnet_id = subnet['SubnetId']
    subnets[subnet_id] = subnet

  # Loop through NAT Gateways and print relevant data.
  for gateway in get_nat_gateways(region):
    # Lookup vpc id and VPC 'name' if it's set
    vpc_id = gateway['VpcId']
    vpc_name = [tag['Value'] for tag in vpcs[vpc_id]['Tags'] if tag['Key'] == 'Name']

    # Lookup subnet id and VPC 'name' if it's set
    subnet_id = gateway['SubnetId']
    subnet_name = [tag['Value'] for tag in subnets[subnet_id]['Tags'] if tag['Key'] == 'Name']
    
    # print NAT gateways with any vpc and subnet info we can find
    print('{}\t{} {}\t{} {}'.format(
      gateway['NatGatewayId'],
      vpc_id, vpc_name,
      subnet_id, subnet_name
    ))
