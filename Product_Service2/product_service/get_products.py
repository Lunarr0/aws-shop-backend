from aws_cdk import (
    aws_lambda as _lambda,
)
from constructs import Construct

def create_list_products_lambda(scope: Construct, id: str,  environment: dict, role: None) -> _lambda.Function:
    return _lambda.Function(
        scope,
        id,
        runtime=_lambda.Runtime.PYTHON_3_9,
        handler='product_list.handler',
        code=_lambda.Code.from_asset('product_service/lambda_func'),
        environment=environment or {}
    )
