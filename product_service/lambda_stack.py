from aws_cdk import Stack
from constructs import Construct
from product_service.get_products import create_list_products_lambda
from product_service.get_product_by_id import create_get_product_lambda

class LambdaStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.list_products_lambda = create_list_products_lambda(
            self, 
            'GetProductsFunction'
        )

        self.get_product_lambda = create_get_product_lambda(
            self, 
            'GetProductByIdFunction'
        )

    @property
    def list_products_function(self):
        return self.list_products_lambda

    @property
    def get_product_function(self):
        return self.get_product_lambda
