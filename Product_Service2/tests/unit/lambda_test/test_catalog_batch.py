# tests/test_catalog_batch_process.py
import unittest
from unittest.mock import patch, MagicMock
import json
import os

@patch('Product_Service2.product_service.lambda_func.catalog_batch.sns')
@patch('Product_Service2.product_service.lambda_func.catalog_batch.dynamodb')
class TestCatalogBatchProcess(unittest.TestCase):
    def setUp(self):
        # Set environment variables
        os.environ['SNS_TOPIC_ARN'] = 'arn:aws:sns:us-east-1:123456789012:test-topic'
        os.environ['PRODUCTS_TABLE_NAME'] = 'products'
        os.environ['STOCKS_TABLE_NAME'] = 'stocks'

    def test_successful_processing(self, mock_dynamodb, mock_sns):
        # Prepare test data
        test_event = {
            'Records': [{
                'body': json.dumps({
                    'title': 'Test Product',
                    'description': 'Test Description',
                    'price': 150,
                    'count': 10
                })
            }]
        }

        # Configure mock successful response
        mock_dynamodb.transact_write_items.return_value = {'ResponseMetadata': {'RequestId': '1234'}}

        # Import lambda_handler here after mocks are in place
        from Product_Service2.product_service.lambda_func.catalog_batch import lambda_handler
        
        # Execute lambda
        response = lambda_handler(test_event, None)

        # Assert DynamoDB transact_write_items was called
        mock_dynamodb.transact_write_items.assert_called_once()
        
        # Assert SNS publish was called
        mock_sns.publish.assert_called_once()
        
        # Verify the response
        self.assertEqual(response['statusCode'], 200)

    def test_multiple_records_processing(self, mock_dynamodb, mock_sns):
        # Test processing multiple records
        test_event = {
            'Records': [
                {
                    'body': json.dumps({
                        'title': 'Product 1',
                        'description': 'Description 1',
                        'price': 150,
                        'count': 10
                    })
                },
                {
                    'body': json.dumps({
                        'title': 'Product 2',
                        'description': 'Description 2',
                        'price': 50,
                        'count': 5
                    })
                }
            ]
        }

        # Configure mock successful response
        mock_dynamodb.transact_write_items.return_value = {'ResponseMetadata': {'RequestId': '1234'}}

        # Import lambda_handler here after mocks are in place
        from Product_Service2.product_service.lambda_func.catalog_batch import lambda_handler
        
        response = lambda_handler(test_event, None)
        
        # Assert DynamoDB transact_write_items was called twice (once for each record)
        self.assertEqual(mock_dynamodb.transact_write_items.call_count, 2)
        
        # Assert SNS publish was called once with both products
        mock_sns.publish.assert_called_once()
        self.assertEqual(response['statusCode'], 200)

    def test_error_handling(self, mock_dynamodb, mock_sns):
        mock_dynamodb.transact_write_items.side_effect = Exception("Test error")

        test_event = {
            'Records': [{
                'body': json.dumps({
                    'title': 'Test Product',
                    'description': 'Test Description',
                    'price': 150,
                    'count': 10
                })
            }]
        }

        #import lambda_handler here after mocks are in place
        from Product_Service2.product_service.lambda_func.catalog_batch import lambda_handler


       # The lambda should NOT raise the exception (it catches it internally)
        response = lambda_handler(test_event, None)

        # Assert DynamoDB transact_write_items was called
        mock_dynamodb.transact_write_items.assert_called_once()

        #Since the error is caught internally, then no products are added to successful_products
        mock_sns.publish.assert_called_once_with(
        TopicArn=os.environ['SNS_TOPIC_ARN'],
            Subject='Products Created Successfully',
            Message=mock_sns.publish.call_args[1]['Message'],  # Dynamic message content
            MessageAttributes={
                'price': {
                    'DataType': 'Number',
                    'StringValue': '150'
                }
            }
        )

        #verify the response is still 200 (function handles errors gracefully)
        self.assertEqual(response['statusCode'], 200)


    def test_invalid_message_format(self, mock_dynamodb, mock_sns):
        test_event = {
            'Records': [{
                'body': json.dumps({
                    'invalid': 'format'
                })
            }]
        }

        # Import lambda_handler here after mocks are in place
        from Product_Service2.product_service.lambda_func.catalog_batch import lambda_handler
        
        # Should raise KeyError due to missing required fields
        with self.assertRaises(KeyError):
            lambda_handler(test_event, None)

    def tearDown(self):
        # Clean up environment variables
        os.environ.pop('SNS_TOPIC_ARN', None)
        os.environ.pop('PRODUCTS_TABLE_NAME', None)
        os.environ.pop('STOCKS_TABLE_NAME', None)
