#!/bin/bash
set -e

# Source environment variables
source /home/dynamodblocal/.env

# Start DynamoDB in the background
java -jar DynamoDBLocal.jar -sharedDb -port $PORT &

# Wait for DynamoDB to start
sleep 5

# Run initialization script
/home/dynamodblocal/init_dynamodb.sh

# Keep container running
echo "DynamoDB is running on port $PORT"
tail -f /dev/null
