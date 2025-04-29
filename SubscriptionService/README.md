## Database Configuration

You can choose between **PostgreSQL** or **DynamoDB** as your database by setting the appropriate value in your `.env` file.

### Using DynamoDB

Before selecting DynamoDB, ensure your DynamoDB infrastructure is deployed.  
Navigate to the `/Localstack` directory and run the deploy script provided there.

### Using PostgreSQL

PostgreSQL will automatically create the necessary tables on startup—no manual setup required.

---

> **Tip:** Always verify your `.env` configuration matches your intended database before starting the service.