from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
     aws_iam as iam,
    aws_dynamodb as dynamodb,
    aws_lambda_event_sources as lambda_event_sources,  
    Duration
)
from constructs import Construct
from product_service.get_products import create_list_products_lambda
from product_service.get_product_by_id import create_get_product_lambda
from product_service.post_create_product import create_product_lambda
from product_service.catalog_batch_process import create_catalog_batch_process_lambda

class LambdaStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, catalog_items_queue=None, create_product_topic=None,  **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        #Referencing DynamoDB
        products_table = dynamodb.Table.from_table_name(
            self,
            'ProductsTable',
            table_name='products'
        )

        stocks_table = dynamodb.Table.from_table_name(
            self,
            'StocksTable',
            table_name='stocks'
        )

        print(f"Products Table Name: {products_table.table_name}")
        print(f"Stocks Table Name: {stocks_table.table_name}")

         # Create Lambda role with explicit permissions
        lambda_role = iam.Role(
            self, 'ProductsLambdaRole',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com')
        )

        # Add CloudWatch Logs permissions
        lambda_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                'service-role/AWSLambdaBasicExecutionRole'
            )
        )

        # Add DynamoDB permissions
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    'dynamodb:Scan',
                    'dynamodb:GetItem',
                    'dynamodb:Query',
                    'dynamodb:PutItem' 
                ],
                resources=[
                    products_table.table_arn,
                    stocks_table.table_arn
                ]
            )
        )
          # Add SNS permissions
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    'sns:Publish'
                ],
                resources=[create_product_topic.topic_arn]
            )
        )

        # Add SQS permissions
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    'sqs:ReceiveMessage',
                    'sqs:SendMessage',
                    'sqs:DeleteMessage',
                    'sqs:GetQueueAttributes'
                ],
                resources=[catalog_items_queue.queue_arn]
            )
        )
        #Creating Lambda functions
        common_env = {
            'PRODUCTS_TABLE_NAME': products_table.table_name,
            'STOCKS_TABLE_NAME': stocks_table.table_name,
            'REGION' : Stack.of(self).region,
            'SQS_QUEUE_URL': catalog_items_queue.queue_url,  
            'SNS_TOPIC_ARN': create_product_topic.topic_arn  
        }

        self.product_lambda = create_product_lambda(
            self,
            'CreateProductFunction',
            environment = common_env,
            role = lambda_role
        )

        self.list_products_lambda = create_list_products_lambda(
            self, 
            'GetProductsFunction',
            environment = common_env,
            role = lambda_role
        )

        self.get_product_lambda = create_get_product_lambda(
            self, 
            'GetProductByIdFunction',
             environment= common_env,
             role = lambda_role
        )

        # Add the catalog batch process Lambda
        self.catalog_batch_process = create_catalog_batch_process_lambda(
            self,
            "CatalogBatchProcess",
            environment= common_env,
            role = lambda_role
        )


         # Add SQS as event source for Lambda
        self.catalog_batch_process.add_event_source(
            lambda_event_sources.SqsEventSource(
                catalog_items_queue,
                batch_size=5,
                max_batching_window=Duration.minutes(1)
            )
        )

         # Granting permissions to Lambda functions
        products_table.grant_read_data(self.list_products_lambda)
        stocks_table.grant_read_data(self.list_products_lambda)
        products_table.grant_read_data(self.get_product_lambda)
        stocks_table.grant_read_data(self.get_product_lambda)
        products_table.grant_write_data(self.product_lambda)
        stocks_table.grant_write_data(self.product_lambda)
        products_table.grant_write_data(self.catalog_batch_process)
        create_product_topic.grant_publish(self.catalog_batch_process)
         # Grant SQS permissions
        catalog_items_queue.grant_consume_messages(self.catalog_batch_process)
        self.catalog_batch_process.add_environment("SQS_QUEUE_URL", catalog_items_queue.queue_url)
        self.catalog_batch_process.add_environment("SNS_TOPIC_ARN", create_product_topic.topic_arn)
        self.catalog_batch_process.add_environment("DYNAMODB_TABLE_NAME", "products")  

    @property
    def list_products_function(self):
        return self.list_products_lambda

    @property
    def get_product_function(self):
        return self.get_product_lambda

    @property
    def product_function(self):
        return self.product_lambda



