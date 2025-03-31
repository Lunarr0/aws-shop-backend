# tests/unit/test_authorization_service.py
import os
import pytest
from aws_cdk import App
from aws_cdk.assertions import Template
from authorization_service.authorization_service_stack import AuthorizationServiceStack

@pytest.fixture
def template():
    app = App()
    stack = AuthorizationServiceStack(app, "TestStack")
    return Template.from_stack(stack)

def test_lambda_function_created(template):
    template.has_resource_properties("AWS::Lambda::Function", {
        "Runtime": "python3.9",
        "Handler": "handler.lambda_handler"
    })

def test_lambda_role_created(template):
    template.has_resource_properties("AWS::IAM::Role", {
        "AssumeRolePolicyDocument": {
            "Statement": [{
                "Action": "sts:AssumeRole",
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                }
            }]
        }
    })
