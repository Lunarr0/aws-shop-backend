""" from aws_cdk import (
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
 """
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
 
         # Common response configurations
         cors_response_parameters = {
             'method.response.header.Access-Control-Allow-Origin': "'*'"
         }
 
         success_response = {
             'statusCode': '200',
             'responseParameters': cors_response_parameters
         }
 
         error_responses = [
             {
                 'statusCode': '400',
                 'responseParameters': cors_response_parameters
             },
             {
                 'statusCode': '500',
                 'responseParameters': cors_response_parameters
             }
         ]
 
         method_responses = [
             {
                 'statusCode': '200',
                 'responseParameters': {
                     'method.response.header.Access-Control-Allow-Origin': True
                 }
             },
             {
                 'statusCode': '400',
                 'responseParameters': {
                     'method.response.header.Access-Control-Allow-Origin': True
                 }
             },
             {
                 'statusCode': '500',
                 'responseParameters': {
                     'method.response.header.Access-Control-Allow-Origin': True
                 }
             }
         ]
 
         # Create API resources and methods
         products = api.root.add_resource('products')
 
         # GET /products
         products.add_method(
             'GET',
             apigw.LambdaIntegration(
                 lambda_stack.list_products_function,
                 proxy=True,
                 integration_responses=[success_response, *error_responses]
             ),
             method_responses=method_responses
         )
 
         # POST /products
         products.add_method(
             'POST',
             apigw.LambdaIntegration(
                 lambda_stack.product_function,
                 proxy=True,
                 integration_responses=[
                     {
                         'statusCode': '201',
                         'responseParameters': cors_response_parameters
                     },
                     *error_responses
                 ]
             ),
             method_responses=[
                 {
                     'statusCode': '201',
                     'responseParameters': {
                         'method.response.header.Access-Control-Allow-Origin': True
                     }
                 },
                 *method_responses[1:]  # Include 400 and 500 responses
             ]
         )
 
         # GET /products/{productId}
         product = products.add_resource('{productId}')
         product.add_method(
             'GET',
             apigw.LambdaIntegration(
                 lambda_stack.get_product_function,
                 proxy=True,
                 integration_responses=[
                     success_response,
                     {
                         'statusCode': '404',
                         'responseParameters': cors_response_parameters
                     },
                     *error_responses
                 ]
             ),
             method_responses=[
                 *method_responses,
                 {
                     'statusCode': '404',
                     'responseParameters': {
                         'method.response.header.Access-Control-Allow-Origin': True
                     }
                 }
             ]
         )
 
         # Output the API URL
         CfnOutput(
             self, "APIGatewayURL",
             value=f"{api.url}products",
             description="API Gateway endpoint URL"
         )
 
         # Output separate endpoints for each operation
         CfnOutput(
             self, "GetProductsURL",
             value=f"{api.url}products",
             description="GET products endpoint URL"
         )
 
         CfnOutput(
             self, "CreateProductURL",
             value=f"{api.url}products",
             description="POST product endpoint URL"
         )
 
         CfnOutput(
             self, "GetProductByIdURL",
             value=f"{api.url}products/{{productId}}",
             description="GET product by ID endpoint URL"
         )
