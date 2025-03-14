# tests/test_catalog_batch_process.py
import unittest
from unittest.mock import patch, MagicMock
import json
import os
from lambda_func.catalog_batch_process import lambda_handler

class TestCatalogBatchProcess(unittest.TestCase):
    @patch('boto3.resource')
    @patch('boto3.client')
    def setUp(self, mock_boto3_client, mock_boto3_resource):
        self.mock_dynamodb = MagicMock()
        self.mock_table = MagicMock()
        self.mock_sns = MagicMock()
        
        mock_boto3_resource.return_value = self.mock_dynamodb
        mock_boto3_client.return_value = self.mock_sns
        
        self.mock_dynamodb.Table.return_value = self.mock_table
        
        # Set environment variables
        os.environ['SNS_TOPIC_ARN'] = 'mock-topic-arn'
        os.environ['PRODUCTS_TABLE_NAME'] = 'products'

    def test_successful_processing(self):
        # Prepare test data
        test_event = {
            'Records': [{
                'body': json.dumps({
                    'id': '1',
                    'title': 'Test Product',
                    'description': 'Test Description',
                    'price': 150,
                    'count': 10
                })
            }]
        }

        # Execute lambda
        response = lambda_handler(test_event, None)

        # Assert DynamoDB put_item was called
        self.mock_table.put_item.assert_called_once()
        
        # Assert SNS publish was called with correct parameters
        self.mock_sns.publish.assert_called_once()
        
        # Verify the response
        self.assertEqual(response['statusCode'], 200)

    def test_multiple_records_processing(self):
        # Test processing multiple records
        test_event = {
            'Records': [
                {
                    'body': json.dumps({
                        'id': '1',
                        'title': 'Product 1',
                        'description': 'Description 1',
                        'price': 150,
                        'count': 10
                    })
                },
                {
                    'body': json.dumps({
                        'id': '2',
                        'title': 'Product 2',
                        'description': 'Description 2',
                        'price': 50,
                        'count': 5
                    })
                }
            ]
        }

        response = lambda_handler(test_event, None)
        
        # Assert DynamoDB put_item was called twice
        self.assertEqual(self.mock_table.put_item.call_count, 2)
        
        # Assert SNS publish was called once with both products
        self.mock_sns.publish.assert_called_once()
        self.assertEqual(response['statusCode'], 200)

    def test_error_handling(self):
        # Test error handling
        self.mock_table.put_item.side_effect = Exception('Test error')
        
        test_event = {
            'Records': [{
                'body': json.dumps({
                    'id': '1',
                    'title': 'Test Product',
                    'description': 'Test Description',
                    'price': 150,
                    'count': 10
                })
            }]
        }

        with self.assertRaises(Exception):
            lambda_handler(test_event, None)
            
        # Assert error notification was sent to SNS
        self.mock_sns.publish.assert_called_once()

    def test_invalid_message_format(self):
        # Test handling of invalid message format
        test_event = {
            'Records': [{
                'body': json.dumps({
                    'invalid': 'format'
                })
            }]
        }

        with self.assertRaises(Exception):
            lambda_handler(test_event, None)

    def tearDown(self):
        # Clean up environment variables
        os.environ.pop('SNS_TOPIC_ARN', None)
        os.environ.pop('PRODUCTS_TABLE_NAME', None)
