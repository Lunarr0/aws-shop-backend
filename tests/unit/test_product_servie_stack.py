import aws_cdk as core
import aws_cdk.assertions as assertions
from product_service.product_service_stack import ProductServiceStack

def test_api_gateway_created():
    # ARRANGE
    app = core.App()
    
    # ACT
    stack = ProductServiceStack(app, "ProductServiceStack")
    template = assertions.Template.from_stack(stack)

    # ASSERT
    template.resource_count_is("AWS::ApiGateway::RestApi", 1)
    template.resource_count_is("AWS::Lambda::Function", 2)
    
    # Verify API Gateway endpoints
    template.has_resource_properties("AWS::ApiGateway::Method", {
        "HttpMethod": "GET",
        "AuthorizationType": "NONE"
    })

def test_lambda_functions_created():
    app = core.App()
    stack = ProductServiceStack(app, "ProductServiceStack")
    template = assertions.Template.from_stack(stack)
    
    # Check Lambda functions
    template.has_resource_properties("AWS::Lambda::Function", {
        "Handler": "product_list.handler",
        "Runtime": "python3.9"
    })
    
    template.has_resource_properties("AWS::Lambda::Function", {
        "Handler": "product_by_id.handler",
        "Runtime": "python3.9"
    })

def test_cors_configuration():
    app = core.App()
    stack = ProductServiceStack(app, "ProductServiceStack")
    template = assertions.Template.from_stack(stack)
    
    # Check CORS configuration
    template.has_resource_properties("AWS::ApiGateway::Method", {
        "HttpMethod": "OPTIONS"
    })
