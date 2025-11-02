import uuid


def test_get_customer_by_customer_id_success(client):
    test_email = "test@example.com"
    create_customer_response = client.post(
        "/customers", json={"email": test_email, "password": "testpass123"}
    ).json()

    customer = create_customer_response["data"]
    get_response = client.get(f"/customers/{customer['id']}")

    assert get_response.status_code == 200
    assert get_response.json()["success"] == True
    assert get_response.json()["message"] == "Customer details fetched successfully"
    assert get_response.json()["data"]["email"] == test_email


def test_get_customer_by_customer_id_invalid_uuid(client):
    invalid_customer_id = "00fe3af9-49d6-4b37-8ba1-49b2129522ed-1234"

    response = client.get(f"/customers/{invalid_customer_id}")

    assert response.status_code == 422
    assert "detail" in response.json()
    assert response.json()["detail"][0]["type"] == "uuid_parsing"
    assert "customer_id" in str(response.json()["detail"])


def test_get_customer_by_customer_id_customer_not_found(client):
    non_existent_customer_id = str(uuid.uuid4())

    response = client.get(f"/customers/{non_existent_customer_id}")

    assert response.status_code == 404
    assert response.json()["message"] == "Customer not found"
