#!/usr/bin/env python3
import os
from aws_cdk import App
from import_service.import_service_stack import ImportServiceStack

app = App()
ImportServiceStack(app, "ImportServiceStack",
    env=dict(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'),
        region=os.getenv('CDK_DEFAULT_REGION')
    )
)

app.synth()
