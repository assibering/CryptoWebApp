<!--
    Documentation:
    This section provides clear instructions for deploying your infrastructure to a LocalStack instance running in a container. 
    The deployment process involves navigating to the appropriate directory and executing the deployment script. 
    **Note:** Deploying infrastructure to a running LocalStack container is essential to simulate real-world AWS cloud behavior in a local development environment.
-->
## Deploying Infrastructure to LocalStack

To deploy your infrastructure to your LocalStack instance running in a container, follow these steps:

1. **Navigate to the `Localstack` directory:**
    ```bash
    cd /Localstack
    ```

2. **Make the deployment script executable and run it:**
    ```bash
    chmod +x deploy-local.sh
    ./deploy-local.sh
    ```

> **Note:** Ensure your LocalStack container is running before executing these commands.
