import json
import pytest
from lambda_func.product_list import handler as list_handler
from lambda_func.product_by_id import handler as get_handler

def test_list_products():
    # ARRANGE
    event = {
        "httpMethod": "GET",
        "path": "/products"
    }
    context = {}

    # ACT
    response = list_handler(event, context)

    # ASSERT
    assert response["statusCode"] == 200
    assert "Access-Control-Allow-Origin" in response["headers"]
    body = json.loads(response["body"])
    assert isinstance(body, list)
    assert len(body) > 0
    assert all(isinstance(product, dict) for product in body)
    assert all("id" in product for product in body)

def test_get_product_by_id_success():
    # ARRANGE
    event = {
        "httpMethod": "GET",
        "path": "/products/1",
        "pathParameters": {"id": "1"}
    }
    context = {}

    # ACT
    response = get_handler(event, context)

    # ASSERT
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["id"] == "1"
    assert "name" in body
    assert "price" in body

def test_get_product_by_id_not_found():
    # ARRANGE
    event = {
        "httpMethod": "GET",
        "path": "/products/999",
        "pathParameters": {"id": "999"}
    }
    context = {}

    # ACT
    response = get_handler(event, context)

    # ASSERT
    assert response["statusCode"] == 404
    body = json.loads(response["body"])
    assert "error" in body

def test_list_products_structure():
    # ARRANGE
    event = {
        "httpMethod": "GET",
        "path": "/products"
    }
    context = {}

    # ACT
    response = list_handler(event, context)
    body = json.loads(response["body"])

    # ASSERT
    for product in body:
        assert set(product.keys()) >= {"id", "name", "price", "description"}
        assert isinstance(product["id"], str)
        assert isinstance(product["name"], str)
        assert isinstance(product["price"], (int, float))
        assert isinstance(product["description"], str)

@pytest.fixture
def api_gateway_event():
    return {
        "resource": "/{proxy+}",
        "path": "/products",
        "httpMethod": "GET",
        "headers": {
            "Accept": "*/*",
            "Content-Type": "application/json"
        },
        "requestContext": {
            "resourceId": "123456",
            "apiId": "1234567890",
            "resourcePath": "/{proxy+}",
            "httpMethod": "GET",
            "requestId": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef",
            "accountId": "123456789012",
            "stage": "prod"
        },
        "pathParameters": None,
        "queryStringParameters": None,
        "body": None
    }

def test_list_products_api_gateway_integration(api_gateway_event):
    # ACT
    response = list_handler(api_gateway_event, {})

    # ASSERT
    assert response["statusCode"] == 200
    assert "body" in response
    assert "headers" in response
    body = json.loads(response["body"])
    assert isinstance(body, list)
