import json
import csv
import boto3
import os
from io import StringIO
import logging


# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        # Get S3 client
        s3_client = boto3.client('s3')
        sqs = boto3.client('sqs')
        
        # Get bucket and file details from the S3 event
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']
        
        print(f"Processing file: {key} from bucket: {bucket}")
        
        # Get the object from S3
        response = s3_client.get_object(Bucket=bucket, Key=key)
        logger.info(f"Reading CSV file from S3: bucket={bucket}, key={key}")
        
        # Read the content of the file
        file_content = response['Body'].read().decode('utf-8')
        
        # Create a StringIO object for CSV parsing
        csv_file = StringIO(file_content)
        
        # Parse CSV
        csv_reader = csv.DictReader(csv_file)
        
        # Process each row
        for row in csv_reader:
            # Log each record
            # print(f"Parsed record: {json.dumps(row)}")
            sqs.send_message(
                QueueUrl=os.environ['SQS_QUEUE_URL'],
                MessageBody=json.dumps(row)
            )
            # logger.info(f"Successfully parsed {len(products)} products from CSV")
            
            
        # Move file to parsed folder
        new_key = key.replace('uploaded/', 'parsed/')
        s3_client.copy_object(
            Bucket=bucket,
            CopySource={'Bucket': bucket, 'Key': key},
            Key=new_key
        )
        
        # Delete the file from uploaded folder
        s3_client.delete_object(Bucket=bucket, Key=key)
        
        return {
            'statusCode': 200,
            'body': json.dumps('CSV processing completed successfully')
        }
        logger.info(f"DynamoDB transaction completed: {json.dumps(response)}")
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error processing file: {str(e)}')
        }
        logger.error(f"Error processing file: {str(e)}")