from aws_cdk import (
    Stack,
    aws_apigateway as apigw,
    CfnOutput
)
from constructs import Construct

class ApiGatewayStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, lambda_stack, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create API Gateway with CORS
        api = apigw.RestApi(
            self, 'ProductsApi',
            rest_api_name='Products Service',
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
                allow_headers=[
                    'Content-Type',
                    'X-Amz-Date',
                    'Authorization',
                    'X-Api-Key',
                    'X-Amz-Security-Token',
                ],
            )
        )

        # Create API resources and methods
        products = api.root.add_resource('products')
        products.add_method(
            'GET',
            apigw.LambdaIntegration(
                lambda_stack.list_products_function,
                proxy=True,
                integration_responses=[{
                    'statusCode': '200',
                    'responseParameters': {
                        'method.response.header.Access-Control-Allow-Origin': "'*'"
                    }
                }]
            ),
            method_responses=[{
                'statusCode': '200',
                'responseParameters': {
                    'method.response.header.Access-Control-Allow-Origin': True
                }
            }]
        )

        product = products.add_resource('{productId}')
        product.add_method(
            'GET',
            apigw.LambdaIntegration(
                lambda_stack.get_product_function,
                proxy=True,
                integration_responses=[{
                    'statusCode': '200',
                    'responseParameters': {
                        'method.response.header.Access-Control-Allow-Origin': "'*'"
                    }
                }]
            ),
            method_responses=[{
                'statusCode': '200',
                'responseParameters': {
                    'method.response.header.Access-Control-Allow-Origin': True
                }
            }]
        )

        # Output the API URL
        CfnOutput(
            self, "APIGatewayURL",
            value=f"{api.url}products",
            description="API Gateway endpoint URL"
        )
