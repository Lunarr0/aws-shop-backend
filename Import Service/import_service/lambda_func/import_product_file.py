import json
import os
import boto3
from botocore.config import Config
from urllib.parse import unquote

def lambda_handler(event, context):
    try:
        # Get the query parameter
        file_name = event['queryStringParameters']['name']
        
        # Decode the filename in case it's URL encoded
        file_name = unquote(file_name)
        
        # Configure S3 client with custom configuration
        config = Config(
            signature_version='v4',
            region_name=os.environ['AWS_REGION']
        )
        s3_client = boto3.client('s3', config=config)
        
        # Generate signed URL
        bucket_name = os.environ['BUCKET_NAME']
        key = f'uploaded/{file_name}'
        
        signed_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': key,
                'ContentType': 'text/csv'
            },
            ExpiresIn=3600  # URL expires in 1 hour
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True,
                'Access-Control-Allow-Methods' : 'OPTIONS,GET,POST,PUT,DELETE',
            },
            'body': signed_url
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True
            },
            'body': json.dumps({'error': str(e)})
        }
