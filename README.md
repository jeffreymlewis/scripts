# Random Scripts
This is a collection of random scripts that make my life easier.

## Configure local helm home
The [Gruntwork Reference Architecture](https://gruntwork.io/reference-architecture/) deploys tiller to [AWS EKS](https://aws.amazon.com/eks/) clusters 
using [terraform](https://www.terraform.io/). This script configures helm home so the [helm](https://github.com/helm/helm) cli can communicate 
with a the tiller deployed in EKS.

You should **NOT** use the helm cli to deploy or modify helm chart directly! It should only be used to view currently deployed objects.
All helm chart changes should be via terraform.

### To use this script

aws auth ...
configure-local-helm-home.sh
. /Users/$USER/gruntwork-helm-home/env  # source env variables
helm version  # should see client **and** server version

