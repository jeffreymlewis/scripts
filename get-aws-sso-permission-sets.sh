#!/bin/bash
# Emit AWS SSO principals and IAM policies for all AWS SSO permission sets
#
# REQUIRED:
# - https://stedolan.github.io/jq/
# - File named `account-ids.txt` containing a mapping of all aws account IDs to friendly names.
set -euC -o pipefail

INSTANCE_ARN="arn:aws:sso:::instance/ssoins-1234567890abcdef"
permission_sets=$(aws sso-admin list-permission-sets --instance-arn "$INSTANCE_ARN" | jq -r '.PermissionSets | @tsv')

sso-admin () {
  aws sso-admin $@ --instance-arn "$INSTANCE_ARN"
}

for permission_set in $permission_sets; do
  echo "###"
  echo "### $(sso-admin describe-permission-set --permission-set-arn $permission_set | jq -r .PermissionSet.Name)"
  echo "###"
  # get list of AWS accounts using this permission set
  account_ids=$(sso-admin list-accounts-for-provisioned-permission-set --permission-set-arn "$permission_set" | jq -r '.AccountIds | @tsv')
  for account_id in $account_ids; do
    # print principals mapped to this permission set in this account
    echo -n "$(grep $account_id account-ids.txt) "
    sso-admin list-account-assignments --permission-set-arn "$permission_set" --account-id "$account_id" | jq -r '.AccountAssignments[] | "\(.PrincipalType) \(.PrincipalId)"'
  done # account_ids
  echo "POLICIES"
  sso-admin list-managed-policies-in-permission-set --permission-set-arn "$permission_set" | jq -r '.AttachedManagedPolicies[] | "\(.Name) \(.Arn)"'
  echo
  sso-admin get-inline-policy-for-permission-set --permission-set-arn "$permission_set" | jq -r .InlinePolicy | jq
  echo   
done # permission_sets
