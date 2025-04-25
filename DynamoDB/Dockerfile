# Build stage - use secrets to set up DynamoDB
FROM amazon/dynamodb-local:latest AS build-stage

# Install AWS CLI
USER root
RUN apt-get update && \
    apt-get install -y python3 python3-pip curl && \
    pip3 install awscli && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy initialization script
COPY init-dynamodb.sh /home/dynamodblocal/init-dynamodb.sh
RUN chmod +x /home/dynamodblocal/init-dynamodb.sh

# Final stage - copy only what's needed
FROM amazon/dynamodb-local:latest

# Copy any necessary files from build stage
COPY --from=build-stage /home/dynamodblocal/init-dynamodb.sh /home/dynamodblocal/
COPY entrypoint.sh /home/dynamodblocal/
RUN chmod +x /home/dynamodblocal/entrypoint.sh

ENTRYPOINT ["/home/dynamodblocal/entrypoint.sh"]
