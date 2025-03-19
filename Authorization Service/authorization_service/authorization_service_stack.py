# authorization_service/authorization_service_stack.py
from aws_cdk import (
    Stack,
    CfnOutput,
    aws_lambda as _lambda,
    aws_iam as iam,
)
from constructs import Construct
import os
import dotenv

class AuthorizationServiceStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        dotenv.load_dotenv()
        CREDENTIALS = "Lunarr0"
        CREDENTIALS_PASSWORD = os.getenv(CREDENTIALS)
        # Create Basic Authorizer Lambda
        basic_authorizer = _lambda.Function(
            self, 'BasicAuthorizerFunction',
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler='handler.lambda_handler',
            code=_lambda.Code.from_asset('authorization_service/lambda_func/basic_authorizer'),
            environment={
                CREDENTIALS: CREDENTIALS_PASSWORD
            },
            function_name='AuthFunction'
        )

        # Add necessary permissions
        basic_authorizer.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    'execute-api:Invoke'
                ],
                resources=['*']
            )
        )

        # Export the Lambda ARN and function name
        CfnOutput(
            self, 'BasicAuthorizerLambdaArn',
            value=basic_authorizer.function_arn,
            export_name='BasicAuthorizerLambdaArn'
        )

        CfnOutput(
            self, 'BasicAuthorizerFunctionName',
            value=basic_authorizer.function_name,
            export_name='BasicAuthorizerFunctionName'
        )
