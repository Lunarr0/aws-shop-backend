from aws_cdk import (
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_s3 as s3,
    Duration
)
from constructs import Construct

def create_import_products_lambda(
    scope: Construct, 
    import_bucket: s3.IBucket
) -> _lambda.Function:
    
    # Create importProductsFile Lambda
    import_products_file = _lambda.Function(
        scope, 'ImportProductsFile',
        runtime=_lambda.Runtime.PYTHON_3_9,
        handler='import_product_file.lambda_handler',
        code=_lambda.Code.from_asset('import_service/lambda_func/'),
        environment={
            'BUCKET_NAME': import_bucket.bucket_name
        },
        timeout=Duration.seconds(30),
        memory_size=128
    )

    # Grant S3 permissions to Lambda
    import_bucket.grant_read_write(import_products_file)
    import_bucket.grant_put(import_products_file)

    # Add additional S3 permissions for URL signing
    import_products_file.add_to_role_policy(
        iam.PolicyStatement(
            actions=['s3:PutObject'],
            resources=[f'{import_bucket.bucket_arn}/*']
        )
    )

    return import_products_file
