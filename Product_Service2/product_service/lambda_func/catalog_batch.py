import json
import os
import boto3
import uuid
import logging
from typing import Dict, Any

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Use boto3 client for DynamoDB
dynamodb = boto3.client('dynamodb')
sns = boto3.client('sns')
sns_topic_arn = os.environ['SNS_TOPIC_ARN']

def lambda_handler(event: Dict[str, Any], context):
    try:
        successful_products = []
        
        # Process each record in the SQS batch
        for record in event['Records']:
            # Parse the message body
            message = json.loads(record['body'])
            
            # Generate product ID
            product_id = str(uuid.uuid4())
            # Create product in DynamoDB
            product = {
                'id': {'S': product_id},  # 'S' indicates the data type is string
                'title': {'S': message['title']},
                'description': {'S': message['description']},
                'price': {'N': str(message['price'])}  # 'N' indicates the data type is number
            }

            count = {
                'product_id': {'S': product_id},
                'count': {'N': str(message['count'])}
            }
            
            sns_product = {
                'id': product_id,
                'title': message['title'],
                'price': message['price'],
                'description': message['description'],
                'count': message['count']
            }

            successful_products.append(sns_product)

            # Transaction write with error handling
            try:
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
                                'Item': count
                            }
                        }
                    ]
                )
                logger.info(f"DynamoDB transaction completed: {json.dumps(response)}")
                print(f"Successfully processed product: {product['id']['S']}")
            except Exception as db_error:
                logger.error(f"Error writing to DynamoDB: {str(db_error)}")
                continue  # Skip this record if there's an error

        # Send notification to SNS topic
        if successful_products:
            sns_message = {
                'message': 'Products were successfully created',
                'products': successful_products
            }
            
            price = successful_products[0]['price'] if successful_products else "0"
            try:
                response = sns.publish(
                    TopicArn=sns_topic_arn,
                    Subject='Products Created Successfully',
                    Message=json.dumps(sns_message, indent=2),
                    MessageAttributes={
                        "price": {
                            "DataType": "Number",
                            "StringValue": str(price)
                        }
                    }
                )
                logger.info(f"SNS notification sent: {response['MessageId']}")
            except Exception as sns_error:
                logger.error(f"Error publishing to SNS: {str(sns_error)}")
            
        return {
            'statusCode': 200,
            'body': json.dumps('Successfully processed batch of products')
        }
        
    except Exception as e:
        error_message = f"Error processing batch: {str(e)}"
        print(error_message)
        
        # Send error notification
        sns.publish(
            TopicArn=sns_topic_arn,
            Subject='Error Creating Products',
            Message=error_message
        )
        
        raise e
