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

def batch_write_items(table, items: List[Dict]):
    """Write items in batches"""
    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)

def populate_tables():
    try:
        dynamodb = get_dynamodb_resource()
        
        # Verify tables exist
        if not verify_tables([PRODUCTS_TABLE, STOCKS_TABLE], dynamodb):
            return
        
        # Get table references
        products_table = dynamodb.Table(PRODUCTS_TABLE)
        stocks_table = dynamodb.Table(STOCKS_TABLE)

        # Sample product data
        products = [
            {"title": "Vegan Protein Powder", "description": "Organic plant-based protein.", "price": 29},
            {"title": "Almond Butter", "description": "Smooth and natural almond butter.", "price": 12},
            {"title": "Quinoa Pasta", "description": "Gluten-free quinoa pasta.", "price": 8}
        ]

        # Prepare items for batch writing
        product_items = []
        stock_items = []

        for product in products:
            product_id = str(uuid.uuid4())
            
            product_items.append({
                "id": product_id,
                "title": product["title"],
                "description": product["description"],
                "price": product["price"]
            })
            
            stock_items.append({
                "product_id": product_id,
                "count": 10  # Default stock count
            })

        # Batch write products
        print("📝 Writing products...")
        batch_write_items(products_table, product_items)
        
        # Batch write stocks
        print("📝 Writing stocks...")
        batch_write_items(stocks_table, stock_items)

        print("\n🎉 All data inserted successfully!")

    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"❌ AWS Error ({error_code}): {error_message}")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    populate_tables()
