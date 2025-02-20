from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    CfnOutput
)
from constructs import Construct

class ProductServiceStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create Lambda functions
        list_products_lambda = _lambda.Function(
            self, 'ListProductsFunction',
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler='product_list.handler',
            code=_lambda.Code.from_asset('product_service/lambda_func')
        )

        get_product_lambda = _lambda.Function(
            self, 'GetProductByIdFunction',
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler='product_by_id.handler',
            code=_lambda.Code.from_asset('product_service/lambda_func')
        )

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
                # max_age=Duration.seconds(300)
            )
        )

        # Create API resources and methods
        products = api.root.add_resource('products')
        products.add_method(
            'GET',
            apigw.LambdaIntegration(
                list_products_lambda,
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

        product = products.add_resource('{id}')
        product.add_method(
            'GET',
            apigw.LambdaIntegration(
                get_product_lambda,
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
