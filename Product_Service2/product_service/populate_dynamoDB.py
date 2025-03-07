import boto3
import uuid
from botocore.exceptions import ClientError
from typing import List, Dict
import os
from dotenv import load_dotenv

#Load enviroment variable from  .env file
load_dotenv()

# Get environment variables with fallback values
REGION = os.getenv('AWS_REGION', 'us-east-1')
PRODUCTS_TABLE = os.getenv('PRODUCTS_TABLE_NAME', 'products')
STOCKS_TABLE = os.getenv('STOCKS_TABLE_NAME', 'stocks')

def get_dynamodb_resource():
    """Initialize DynamoDB resource with credentials from environment"""
    return boto3.resource('dynamodb', region_name=REGION)

def verify_tables(tables: List[str], dynamodb) -> bool:
    """Verify if all required tables exist"""
    existing_tables = list(dynamodb.tables.all())
    existing_table_names = [table.name for table in existing_tables]
    
    for table in tables:
        if table not in existing_table_names:
            print(f"❌ Table {table} does not exist")
            return False
    return True

def create_products_with_transactions(dynamodb, products):
    """Create products and stocks using transactions"""
    try:
        for product in products:
            product_id = str(uuid.uuid4())
            
            # Create transaction items
            transaction_items = [
                {
                    'Put': {
                        'TableName': PRODUCTS_TABLE,
                        'Item': {
                            'id': product_id,
                            'title': product['title'],
                            'description': product['description'],
                            'price': product['price']
                        }
                    }
                },
                {
                    'Put': {
                        'TableName': STOCKS_TABLE,
                        'Item': {
                            'product_id': product_id,
                            'count': 10
                        }
                    }
                }
            ]
            
            # Execute transaction
            dynamodb.meta.client.transact_write_items(
                TransactItems=transaction_items
            )
            print(f"✅ Created product and stock for {product['title']}")

    except ClientError as e:
        if e.response['Error']['Code'] == 'TransactionCanceledException':
            print("❌ Transaction cancelled:", e.response['CancellationReasons'])
        raise

def populate_tables():
    try:
        dynamodb = get_dynamodb_resource()
        
        # Verify tables exist
        if not verify_tables([PRODUCTS_TABLE, STOCKS_TABLE], dynamodb):
            return
        
        # Sample product data
        products = [
            {"title": "Vegan Protein Powder", "description": "Organic plant-based protein.", "price": 29},
            {"title": "Almond Butter", "description": "Smooth and natural almond butter.", "price": 12},
            {"title": "Quinoa Pasta", "description": "Gluten-free quinoa pasta.", "price": 8}
        ]

        # Create products using transactions
        create_products_with_transactions(dynamodb, products)
        print("\n🎉 All data inserted successfully!")

    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"❌ AWS Error ({error_code}): {error_message}")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    populate_tables()
