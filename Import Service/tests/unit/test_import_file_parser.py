import unittest
from unittest.mock import patch, MagicMock, call
import json
from lambda.import_file_parser import lambda_handler

class TestImportFileParser(unittest.TestCase):
    @patch('lambda.import_file_parser.boto3.client')
    def test_successful_csv_processing(self, mock_boto3_client):
        # Mock S3 client and its methods
        mock_s3_client = MagicMock()
        mock_boto3_client.return_value = mock_s3_client
        
        # Mock S3 get_object response
        mock_s3_client.get_object.return_value = {
            'Body': MagicMock(
                read=lambda: b'title,description,price\nProduct1,Desc1,10.99\nProduct2,Desc2,20.99'
            )
        }

        # Mock event
        event = {
            'Records': [{
                's3': {
                    'bucket': {'name': 'myimportservicebucket'},
                    'object': {'key': 'uploaded/test.csv'}
                }
            }]
        }

        # Call the lambda handler
        response = lambda_handler(event, {})

        # Assert successful response
        self.assertEqual(response['statusCode'], 200)
        
        # Verify S3 operations were called correctly
        mock_s3_client.get_object.assert_called_once_with(
            Bucket='myimportservicebucket',
            Key='uploaded/test.csv'
        )
        
        # Verify file was copied to parsed folder
        mock_s3_client.copy_object.assert_called_once_with(
            Bucket='myimportservicebucket',
            CopySource={'Bucket': 'myimportservicebucket', 'Key': 'uploaded/test.csv'},
            Key='parsed/test.csv'
        )
        
        # Verify original file was deleted
        mock_s3_client.delete_object.assert_called_once_with(
            Bucket='myimportservicebucket',
            Key='uploaded/test.csv'
        )

    @patch('lambda.import_file_parser.boto3.client')
    def test_invalid_csv_format(self, mock_boto3_client):
        # Mock S3 client with invalid CSV content
        mock_s3_client = MagicMock()
        mock_boto3_client.return_value = mock_s3_client
        mock_s3_client.get_object.return_value = {
            'Body': MagicMock(
                read=lambda: b'invalid,csv,format\nwithout,proper,headers'
            )
        }

        # Mock event
        event = {
            'Records': [{
                's3': {
                    'bucket': {'name': 'test-bucket'},
                    'object': {'key': 'uploaded/test.csv'}
                }
            }]
        }

        # Call the lambda handler
        response = lambda_handler(event, {})

        # Assert error response
        self.assertEqual(response['statusCode'], 500)

    @patch('lambda.import_file_parser.boto3.client')
    def test_s3_error_handling(self, mock_boto3_client):
        # Mock S3 client to raise an exception
        mock_s3_client = MagicMock()
        mock_boto3_client.return_value = mock_s3_client
        mock_s3_client.get_object.side_effect = Exception('S3 Error')

        # Mock event
        event = {
            'Records': [{
                's3': {
                    'bucket': {'name': 'test-bucket'},
                    'object': {'key': 'uploaded/test.csv'}
                }
            }]
        }

        # Call the lambda handler
        response = lambda_handler(event, {})

        # Assert error response
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('S3 Error', json.loads(response['body'])['error'])
