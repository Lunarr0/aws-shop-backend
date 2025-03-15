from aws_cdk import (
    Stack,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as sns_subscriptions,
    Duration
)
from constructs import Construct
from product_service.lambda_stack import LambdaStack
from product_service.api_gateway_stack import ApiGatewayStack
import os

# from jinja2 import Environment

class ProductServiceStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

         # Create SQS Queue
        self.catalog_items_queue = sqs.Queue(
            self, 
            "CatalogItemsQueue",
            queue_name="catalogItemsQueue",
            visibility_timeout=Duration.seconds(30)
        )


        # Create SNS Topic
        self.create_product_topic = sns.Topic(
            self,
            "CreateProductTopic",
            topic_name="createProductTopic"
        )

        # Add email subscription for high-priced items (price >= 100)
        self.create_product_topic.add_subscription(
            sns_subscriptions.EmailSubscription(
                "oluwalunar.misc@gmail.com",
                 filter_policy={
                    "price": sns.SubscriptionFilter.numeric_filter(
                        greater_than_or_equal_to = 100
                    )
                }
             )
        )

        # Add email subscription for low-priced items (price < 100)
        self.create_product_topic.add_subscription(
            sns_subscriptions.EmailSubscription(
                "oluwalunar@gmail.com",
                filter_policy={
                    "price": sns.SubscriptionFilter.numeric_filter(
                        less_than = 100
                    )
                }
            )
        )

        # Create Lambda Stack
        lambda_stack = LambdaStack(
            self, 
            "ProductLambdaStack",
            catalog_items_queue=self.catalog_items_queue,
            create_product_topic=self.create_product_topic
           
            )

        # Create API Gateway Stack
        api_gateway_stack = ApiGatewayStack(
            self, 
            "ProductApiGatewayStack",
            lambda_stack=lambda_stack
        )
