import json
import os
import boto3
from decimal import Decimal
from typing import Dict, Any, Optional

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def get_product_by_id(dynamodb, product_id: str) -> Optional[Dict[str, Any]]:
    """Get product from DynamoDB by ID"""
    table = dynamodb.Table(os.environ['PRODUCTS_TABLE_NAME'])
    response = table.get_item(
        Key={'id': product_id}
    )
    return response.get('Item')

def get_stock_by_product_id(dynamodb, product_id: str) -> Optional[Dict[str, Any]]:
    """Get stock information from DynamoDB by product ID"""
    table = dynamodb.Table(os.environ['STOCKS_TABLE_NAME'])
    response = table.get_item(
        Key={'product_id': product_id}
    )
    return response.get('Item')

def create_response(status_code: int, body: Any) -> Dict[str, Any]:
    """Create API Gateway response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        },
        'body': json.dumps(body, cls=DecimalEncoder)
    }

def handler(event, context):
    try:
        # Log the incoming event
        print(f"Event: {json.dumps(event)}")
        
        # Get product ID from path parameters
        product_id = event.get('pathParameters', {}).get('productId')
        
        if not product_id:
            return create_response(400, {'message': 'Product ID is required'})

        # Initialize DynamoDB client
        dynamodb = boto3.resource('dynamodb', region_name=os.environ['REGION'])
        
        # Get product details
        product = get_product_by_id(dynamodb, product_id)
        
        if not product:
            return create_response(404, {'message': 'Product not found'})
        
        # Get stock information
        stock = get_stock_by_product_id(dynamodb, product_id)
        
        # Add stock count to product
        product['count'] = stock['count'] if stock else 0
        
        # Return successful response
        return create_response(200, product)
        
    except Exception as e:
        print(f"Error: {str(e)}")  # Log the error
        return create_response(500, {'message': f'Internal server error: {str(e)}'})
