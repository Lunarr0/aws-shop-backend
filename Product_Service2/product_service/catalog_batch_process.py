# product_service/catalog_batch_process.py
from aws_cdk import (
    aws_lambda as _lambda,
    Duration
)
from constructs import Construct

def create_catalog_batch_process_lambda(scope: Construct, 
            id: str, environment: dict, role: None) -> _lambda.Function:
    return _lambda.Function(
        scope,
        id,
        runtime=_lambda.Runtime.PYTHON_3_9,
        handler="lambda_handler",
        code=_lambda.Code.from_asset("product_service/lambda_func"),
        environment=environment,
        role=role,
        timeout=Duration.seconds(30),
        memory_size=256
    )
