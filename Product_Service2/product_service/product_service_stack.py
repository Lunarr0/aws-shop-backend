from aws_cdk import Stack
from constructs import Construct
from product_service.lambda_stack import LambdaStack
from product_service.api_gateway_stack import ApiGatewayStack

class ProductServiceStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create Lambda Stack
        lambda_stack = LambdaStack(self, "ProductLambdaStack")

        # Create API Gateway Stack
        api_gateway_stack = ApiGatewayStack(
            self, 
            "ProductApiGatewayStack",
            lambda_stack=lambda_stack
        )
