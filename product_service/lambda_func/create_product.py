import json
import os
import boto3
import uuid
from decimal import Decimal
from typing import Dict, Any

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def create_response(status_code: int, body: Any) -> Dict[str, Any]:
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'OPTIONS,POST'
        },
        'body': json.dumps(body, cls=DecimalEncoder)
    }

def validate_product_data(data: Dict) -> tuple[bool, str]:
    """Validate product data"""
    if not data:
        return False, "Request body is empty"
    
    required_fields = ['title', 'description', 'price', 'count']
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    if not isinstance(data['price'], (int, float)) or data['price'] <= 0:
        return False, "Price must be a positive number"
    
    if not isinstance(data['count'], int) or data['count'] < 0:
        return False, "Count must be a non-negative integer"
    
    return True, ""

def handler(event, context):
    try:
        print(f"Received event: {event}")
        print(f"Context: RequestId: {context.aws_request_id}")

        # Parse request body
        body = event.get('body', '{}')
        if isinstance(body, str):
            body = json.loads(body)

        print(f"Validating product data: {body}")
        
        # Validate request data
        is_valid, error_message = validate_product_data(body)
        if not is_valid:
            print(f"Validation failed: {error_message}")
            return create_response(400, {'message': error_message})

        # Generate unique ID for the product
        product_id = str(uuid.uuid4())

        # Prepare product data
        product_data = {
            'id': product_id,
            'title': body['title'],
            'description': body['description'],
            'price': Decimal(str(body['price']))
        }

        stock_data = {
            'product_id': product_id,
            'count': body['count']
        }

        # Initialize DynamoDB
        dynamodb = boto3.resource('dynamodb', region_name=os.environ['REGION'])
        products_table = dynamodb.Table(os.environ['PRODUCTS_TABLE_NAME'])
        stocks_table = dynamodb.Table(os.environ['STOCKS_TABLE_NAME'])

        # Save to DynamoDB
        print(f"Saving product: {product_data}")
        products_table.put_item(Item=product_data)
        
        print(f"Saving stock: {stock_data}")
        stocks_table.put_item(Item=stock_data)

        # Combine product and stock data for response
        response_data = {**product_data, 'count': stock_data['count']}
        
        print(f"Successfully created product with ID: {product_id}")
        return create_response(201, {
            'message': 'Product created successfully',
            'product': response_data
        })

    except json.JSONDecodeError as e:
        print(f"JSON decode error: {str(e)}")
        return create_response(400, {'message': 'Invalid JSON in request body'})
    except Exception as e:
        print(f"Error: {str(e)}")
        return create_response(500, {'message': f'Internal server error: {str(e)}'})
