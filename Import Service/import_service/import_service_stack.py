from aws_cdk import (
    Stack,
    aws_s3 as s3,
)
from constructs import Construct
from .api_gateway import create_api_gateway
from .import_products_lambda import create_import_products_lambda
from .parse_products_lambda import create_parse_products_lambda

class ImportServiceStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Reference existing S3 bucket
        import_bucket = s3.Bucket.from_bucket_name(
            self, 'ImportBucket',
            bucket_name='myimportservicebucket'
        )

        # Create Lambda functions
        import_products_lambda = create_import_products_lambda(
            self, 
            import_bucket
        )

        parse_products_lambda = create_parse_products_lambda(
            self, 
            import_bucket
        )

        # Create API Gateway
        api = create_api_gateway(
            self, 
            import_products_lambda
        )

        
