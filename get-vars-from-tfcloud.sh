#!/bin/bash
set -euC -o pipefail

die() {
  echo "$0: $*" >&2
  usage
  exit 2
}

usage() {
  echo "Usage: $0 [Options] --token=TOKEN --workspace_name=NAME --org_name=NAME"
  echo "  Required:"
  echo "    --token  Terraform Cloud bearer token (look in your ~/.terraformrc)"
  echo "    --workspace_name  TFC workspace name"
  echo "    --org_name  TFC organization name"
  echo "  Options:"
  echo "    --help            print usage message"
  echo
  exit 2
}

while [ $# -gt 0 ]; do
  case "$1" in
    --token=*) token="${1#*=}"; shift;;
    --workspace_name=*) workspace_name="${1#*=}"; shift;;
    --org_name=*) org_name="${1#*=}"; shift;;
    --help) usage;;

    --token|--workspace_name|--org_name) die "$1 requires an argument";;
    *) die "$1 unknown option"
  esac
done

# required
[ -n "${org_name+x}" ] || die "--org_name is required"
[ -n "${token+x}" ] || die "--token is required"
[ -n "${workspace_name+x}" ] || die "--workspace_name is required"


WORKSPACE_ID=$(curl -s --header "Authorization: Bearer $token" --header "Content-Type: application/vnd.api+json" "https://app.terraform.io/api/v2/organizations/$org_name/workspaces/$workspace_name" | jq -r .data.id)

# GET variables
curl -s --header "Authorization: Bearer $token" --header "Content-Type: application/vnd.api+json" "https://app.terraform.io/api/v2/workspaces/$WORKSPACE_ID/vars" \
 | jq -r '.data[].attributes | "\(.key)=\(.value)"'
