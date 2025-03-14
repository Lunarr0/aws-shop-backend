# lambda_func/catalog_batch_process.py
import json
import os
import boto3
from typing import Dict, Any

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')
table = 'products'


def lambda_handler(event: Dict[str, Any], context):
    try:
       # Get SNS topic ARN from environment variables during runtime
        sns_topic_arn = os.environ.get('SNS_TOPIC_ARN')
        if not sns_topic_arn:
            raise ValueError("SNS_TOPIC_ARN environment variable is not set")

        successful_products = []
        
        # Process each record in the SQS batch
        for record in event['Records']:
            # Parse the message body
            message = json.loads(record['body'])
            
            # Create product in DynamoDB
            product = {
                'id': message['id'],
                'title': message['title'],
                'description': message['description'],
                'price': message['price'],
                'count': message['count']
            }
            
            # Put item in DynamoDB table
            table.put_item(Item=product)
            successful_products.append(product)
            
            print(f"Successfully processed product: {product['id']}")
        
        # Send notification to SNS topic
        if successful_products:
            sns_message = {
                'message': 'Products were successfully created',
                'products': successful_products
            }
            
            sns.publish(
                TopicArn=sns_topic_arn,
                Subject='Products Created Successfully',
                Message=json.dumps(sns_message, indent=2)
            )
            
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
