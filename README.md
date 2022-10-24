# Random Scripts
This is a collection of random scripts that make my life easier.

# get-bucket-size.py
This script returns a list of all S3 buckets sorted by size in bytes. The multiple calls to AWS Cloudwatch makes this very inefficient, but it works.

## Usage

```
python3 get-bucket-size.py
```

# get-vars-from-tfcloud.sh
This simple script pulls workspace variables from Terraform Cloud.

## Usage
The TFC api does not quote string values so you may have to fix
those by quoting. The HCL formatted variables are good to go as-is.
```
./get-vars-from-tfcloud.sh --token="my-tfcloud-bearer-token" --org_name="my_org" --workspace_name="my_workspace" > terraform.tfvars
```
