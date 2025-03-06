from aws_cdk import (
    aws_lambda as _lambda,
    Stack
)
from constructs import Construct
from typing import Dict

def create_product_lambda(
    scope: Construct,  id: str,environment: dict, role: None) -> _lambda.Function:
    """
    Create the createProduct Lambda function
    Args:
        scope: CDK Construct scope
        id: Construct ID
        products_table_name: Name of the products table
        stocks_table_name: Name of the stocks table
    Returns:
        _lambda.Function: The created Lambda function
    """
    return _lambda.Function(
        scope,
        id,
        runtime=_lambda.Runtime.PYTHON_3_9,
        handler='create_product.handler',
        code=_lambda.Code.from_asset('product_service/lambda_func'),
        environment = environment or {}
    )
