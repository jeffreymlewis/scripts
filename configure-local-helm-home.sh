#!/bin/bash
set -euC -o pipefail

# configure a helm home to work with Gruntwork-deployed tiller

# where to create your helm home
HELM_HOME="$1"

# Should get this from kubectl
TILLER_NAMESPACE='kube-system'

# Ex. For ARN arn:aws:sts::111111111111:assumed-role/allow-full-access-from-other-accounts/user_name
# we want this regex to return "allow-full-access-from-other-accounts"
RBAC_ROLE=$(aws sts get-caller-identity | jq -r .Arn | awk -F/ '{print $2}') \

# Dig the "cluster name" out of kubectl config
KUBE_CONTEXT=$(kubectl config current-context)
KUBE_CLUSTER_ARN=$(kubectl config view -o json | jq -r ".contexts[] | select(.name==\"$KUBE_CONTEXT\").context.cluster")
EKS_CLUSTER_NAME=$(echo "$KUBE_CLUSTER_ARN" | awk -F/ '{print $NF}')

kubergrunt helm configure \
  --tiller-namespace $TILLER_NAMESPACE \
  --resource-namespace $TILLER_NAMESPACE \
  --helm-home $HELM_HOME \
  --rbac-user $RBAC_ROLE \
  --kubectl-server-endpoint $(aws eks describe-cluster --name $EKS_CLUSTER_NAME | jq -r .cluster.endpoint) \
  --kubectl-certificate-authority $(aws eks describe-cluster --name=$EKS_CLUSTER_NAME | jq -r .cluster.certificateAuthority.data) \
  --kubectl-token $(aws eks get-token --cluster-name $EKS_CLUSTER_NAME | jq -r .status.token)

