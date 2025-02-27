import json
import os
import boto3
from decimal import Decimal
from typing import Dict, List, Any

# Custom JSON encoder for Decimal types
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def get_products(dynamodb) -> List[Dict[str, Any]]:
    """Get all products from DynamoDB"""
    table = dynamodb.Table(os.environ['PRODUCTS_TABLE_NAME'])
    response = table.scan()
    return response.get('Items', [])

def get_stocks(dynamodb) -> List[Dict[str, Any]]:
    """Get all stocks from DynamoDB"""
    table = dynamodb.Table(os.environ['STOCKS_TABLE_NAME'])
    response = table.scan()
    return response.get('Items', [])

def join_products_with_stocks(products: List[Dict], stocks: List[Dict]) -> List[Dict]:
    """Join products with their stock information"""
    stocks_by_id = {stock['product_id']: stock['count'] for stock in stocks}
    
    for product in products:
        product['count'] = stocks_by_id.get(product['id'], 0)
    
    return products

def create_response(status_code: int, body: Any) -> Dict[str, Any]:
    """Create API Gateway response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        },
        'body': json.dumps(body, cls=DecimalEncoder)  # Used DecimalEncoder here
    }

def handler(event, context):
    try:
        # Initialize DynamoDB client
        dynamodb = boto3.resource('dynamodb', region_name=os.environ['REGION'])
        
        # Get products and stocks
        products = get_products(dynamodb)
        stocks = get_stocks(dynamodb)
        
        # Join products with stocks
        joined_products = join_products_with_stocks(products, stocks)
        
        # Return successful response
        return create_response(200, joined_products)
        
    except Exception as e:
        print(f"Error: {str(e)}")  # Log the error
        return create_response(500, {'message': f'Internal server error: {str(e)}'})
