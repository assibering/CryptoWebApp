#!/bin/bash
set -e

# Source environment variables
source /home/dynamodblocal/.env

echo "Creating DynamoDB users table..."
aws dynamodb create-table \
  --table-name users \
  --attribute-definitions \
    AttributeName=email,AttributeType=S \
  --key-schema \
    AttributeName=email,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
  --endpoint-url http://localhost:$PORT \
  --region $AWS_REGION

echo "DynamoDB users table created successfully."
