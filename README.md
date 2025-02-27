## Environment Variables

The following environment variables are required:

- `AWS_REGION`: AWS region (default: us-east-1)
- `PRODUCTS_TABLE_NAME`: DynamoDB products table name
- `STOCKS_TABLE_NAME`: DynamoDB stocks table name
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret access key

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
