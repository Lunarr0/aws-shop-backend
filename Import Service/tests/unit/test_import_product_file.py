import unittest
from unittest.mock import patch, MagicMock
import json
from lambda.import_product_file import lambda_handler

class TestImportProductFile(unittest.TestCase):
    @patch('lambda.import_product_file.boto3.client')
    def test_successful_url_generation(self, mock_boto3_client):
        # Mock S3 client and its generate_presigned_url method
        mock_s3_client = MagicMock()
        mock_boto3_client.return_value = mock_s3_client
        mock_s3_client.generate_presigned_url.return_value = 'https://test-signed-url'

        # Mock event and context
        event = {
            'queryStringParameters': {
                'name': 'test.csv'
            }
        }
        context = {}

        # Call the lambda handler
        response = lambda_handler(event, context)

        # Assert response structure
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), 'https://test-signed-url')
        
        # Verify S3 client was called correctly
        mock_s3_client.generate_presigned_url.assert_called_once_with(
            'put_object',
            Params={
                'Bucket': 'myimportservicebucket',
                'Key': 'uploaded/test.csv',
                'ContentType': 'text/csv'
            },
            ExpiresIn=3600
        )

    @patch('lambda.import_product_file.boto3.client')
    def test_missing_name_parameter(self, mock_boto3_client):
        # Mock event without name parameter
        event = {
            'queryStringParameters': {}
        }
        context = {}

        # Call the lambda handler
        response = lambda_handler(event, context)

        # Assert error response
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Missing name parameter', json.loads(response['body'])['error'])

    @patch('lambda.import_product_file.boto3.client')
    def test_s3_error_handling(self, mock_boto3_client):
        # Mock S3 client to raise an exception
        mock_s3_client = MagicMock()
        mock_boto3_client.return_value = mock_s3_client
        mock_s3_client.generate_presigned_url.side_effect = Exception('S3 Error')

        # Mock event and context
        event = {
            'queryStringParameters': {
                'name': 'test.csv'
            }
        }
        context = {}

        # Call the lambda handler
        response = lambda_handler(event, context)

        # Assert error response
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('S3 Error', json.loads(response['body'])['error'])
