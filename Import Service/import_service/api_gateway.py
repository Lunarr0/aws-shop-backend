from aws_cdk import (
    aws_apigateway as apigateway,
    aws_lambda as _lambda,
    CfnOutput
)
from constructs import Construct

def create_api_gateway(scope: Construct, import_products_lambda: _lambda.Function) -> apigateway.RestApi:
    # Create API Gateway
    api = apigateway.RestApi(
        scope, 'ImportApi',
        rest_api_name='Import Service API',
        description='API Gateway for Import Service',
        default_cors_preflight_options=apigateway.CorsOptions(
            allow_origins=apigateway.Cors.ALL_ORIGINS,
            allow_methods=apigateway.Cors.ALL_METHODS,
            allow_headers=['Content-Type', 'X-Amz-Date', 
                         'Authorization', 'X-Api-Key'],
            allow_credentials=True
        )
    )

    # Create API resource and method
    import_resource = api.root.add_resource('import')
    
    import_resource.add_method(
        'GET',
        apigateway.LambdaIntegration(import_products_lambda),
        request_parameters={
            'method.request.querystring.name': True
        },
        request_validator_options=apigateway.RequestValidatorOptions(
            validate_request_parameters=True
        )
    )

    # Output the API URL
    CfnOutput(
        scope, 'ApiUrl',
        value=api.url,
        description='API Gateway URL'
    )

    return api
