#!/bin/bash
set -e

cd ./terraform

# Initialize and apply Terraform
terraform init
source ../environments/.env.local && terraform apply -auto-approve

echo "Users table created successfully in LocalStack!"
