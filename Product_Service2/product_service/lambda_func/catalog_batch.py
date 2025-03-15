import json
import os
import boto3
from typing import Dict, Any
import uuid
import logging
import csv
import io

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.client('dynamodb')
sns = boto3.client('sns')
s3 = boto3.client('s3')

def read_csv_from_s3(bucket: str, key: str) -> list:
    """Read and parse CSV file from S3"""
    try:
        logger.info(f"Reading CSV file from S3: bucket={bucket}, key={key}")
        
        # Get the file from S3
        response = s3.get_object(Bucket=bucket, Key=key)
        file_content = response['Body'].read().decode('utf-8')
        
        # Parse CSV content
        products = []
        csv_reader = csv.DictReader(io.StringIO(file_content))
        
        for row in csv_reader:
            try:
                # Validate and clean row data
                product = {
                    'title': row['title'].strip(),
                    'description': row['description'].strip(),
                    'price': float(row['price']),
                    'count': int(row['count'])
                }
                products.append(product)
            except (KeyError, ValueError) as e:
                logger.error(f"Error parsing CSV row: {str(e)}")
                logger.error(f"Row content: {row}")
                continue
                
        logger.info(f"Successfully parsed {len(products)} products from CSV")
        return products
        
    except Exception as e:
        logger.error(f"Error reading CSV from S3: {str(e)}")
        raise

def process_product(product_data: Dict) -> Dict:
    """Process a single product and return the result"""
    try:
        # Generate product ID
        product_id = str(uuid.uuid4())
        logger.info(f"Processing product with generated ID: {product_id}")

        # Prepare DynamoDB items
        product = {
            'id': {'S': product_id},
            'title': {'S': str(product_data['title'])},
            'description': {'S': str(product_data['description'])},
            'price': {'N': str(float(product_data['price']))},
        }

        stock = {
            'product_id': {'S': product_id},
            'count': {'N': str(int(product_data['count']))}
        }

        # Execute DynamoDB transaction
        logger.info(f"Executing DynamoDB transaction for product: {json.dumps(product)}")
        response = dynamodb.transact_write_items(
            TransactItems=[
                {
                    'Put': {
                        'TableName': os.environ['PRODUCTS_TABLE_NAME'],
                        'Item': product
                    }
                },
                {
                    'Put': {
                        'TableName': os.environ['STOCKS_TABLE_NAME'],
                        'Item': stock
                    }
                }
            ]
        )
        logger.info(f"DynamoDB transaction completed: {json.dumps(response)}")

        return {
            'product_id': product_id,
            'title': product_data['title'],
            'description': product_data['description'],
            'price': float(product_data['price']),
            'count': int(product_data['count'])
        }

    except Exception as e:
        logger.error(f"Error processing product: {str(e)}")
        raise

def lambda_handler(event: Dict[str, Any], context):
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Validate environment variables
        required_envs = ['PRODUCTS_TABLE_NAME', 'STOCKS_TABLE_NAME', 'SNS_TOPIC_ARN']
        for env in required_envs:
            if not os.environ.get(env):
                raise ValueError(f"Missing required environment variable: {env}")

        logger.info("Environment variables:")
        logger.info(f"PRODUCTS_TABLE_NAME: {os.environ.get('PRODUCTS_TABLE_NAME')}")
        logger.info(f"STOCKS_TABLE_NAME: {os.environ.get('STOCKS_TABLE_NAME')}")
        logger.info(f"SNS_TOPIC_ARN: {os.environ.get('SNS_TOPIC_ARN')}")

        successful_products = []

        # Process S3 events
        for record in event['Records']:
            try:
                # Verify this is an S3 event
                if record['eventSource'] != 'aws:s3':
                    logger.error(f"Unexpected event source: {record['eventSource']}")
                    continue

                # Get S3 bucket and key
                bucket = record['s3']['bucket']['name']
                key = record['s3']['object']['key']
                logger.info(f"Processing S3 object: bucket={bucket}, key={key}")

                # Read and parse CSV file
                products = read_csv_from_s3(bucket, key)
                
                # Process each product
                for product_data in products:
                    try:
                        processed_product = process_product(product_data)
                        successful_products.append(processed_product)
                        logger.info(f"Successfully processed product: {processed_product['product_id']}")
                    except Exception as product_error:
                        logger.error(f"Error processing product: {str(product_error)}")
                        logger.error(f"Product data: {json.dumps(product_data)}")
                        continue

            except Exception as record_error:
                logger.error(f"Error processing record: {str(record_error)}")
                continue

        # Send SNS notification for successful products
        if successful_products:
            try:
                sns_message = {
                    'message': 'Products were successfully created',
                    'products': successful_products
                }
                
                logger.info(f"Sending SNS notification for {len(successful_products)} products")
                response = sns.publish(
                    TopicArn=os.environ['SNS_TOPIC_ARN'],
                    Subject='Products Created Successfully',
                    Message=json.dumps(sns_message, indent=2)
                )
                logger.info(f"SNS notification sent: {response['MessageId']}")
            except Exception as sns_error:
                logger.error(f"Error publishing to SNS: {str(sns_error)}")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Successfully processed {len(successful_products)} products',
                'products': successful_products
            })
        }

    except Exception as e:
        error_message = f"Fatal error in lambda_handler: {str(e)}"
        logger.error(error_message)
        return {
            'statusCode': 500,
            'body': json.dumps(error_message)
        }
