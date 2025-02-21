from product_service.lambda_func.products_mock import products
import json

def handler(event, context):
    product_id = event['pathParameters']['productId']
    
    product = next(
        (item for item in products if item["id"] == product_id), 
        None
    )
    
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'OPTIONS,GET'
    }
    
    if not product:
        return {
            'statusCode': 404,
            'headers': headers,
            'body': json.dumps({'message': 'Product not found'})
        }
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(product)
    }
