import json
import pytest
from product_service.lambda_func.product_list import handler as list_handler
from product_service.lambda_func.product_by_id import handler as get_handler

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
        "pathParameters": {"productId": "1"}
    }
    context = {}

    # ACT
    response = get_handler(event, context)

    # ASSERT
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["id"] == "1"
    assert "title" in body
    assert "price" in body

def test_get_product_by_id_not_found():
    # ARRANGE
    event = {
        "httpMethod": "GET",
        "path": "/products/999",
        "pathParameters": {"productId": "999"}
    }
    context = {}

    # ACT
    response = get_handler(event, context)

    # ASSERT
    assert response["statusCode"] == 404
    body = json.loads(response["body"])
    assert body["message"] == "Product not found"

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
        assert set(product.keys()) >= {"id", "title", "price", "description"}
        assert isinstance(product["id"], str)
        assert isinstance(product["title"], str)
        assert isinstance(product["price"], (int, float))
        assert isinstance(product["description"], str)


