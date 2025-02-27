from aws_cdk import (
    aws_lambda as _lambda,
)
from constructs import Construct

def create_get_product_lambda(scope: Construct, id: str) -> _lambda.Function:
    return _lambda.Function(
        scope,
        id,
        runtime=_lambda.Runtime.PYTHON_3_9,
        handler='product_by_id.handler',
        code=_lambda.Code.from_asset('product_service/lambda_func')
    )
