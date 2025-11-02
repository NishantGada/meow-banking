import uuid


def test_update_customer_success(client):
    create_customer_response = client.post(
        "/customers", json={"email": "old@example.com", "password": "testpass123"}
    ).json()
    customer_id = create_customer_response["data"]["id"]

    response = client.put(
        f"/customers/{customer_id}", json={"email": "new@example.com"}
    )

    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["data"]["email"] == "new@example.com"
    assert response.json()["message"] == "Email updated successfully"

    # Now verifying if the changed email persists
    get_response = client.get(f"/customers/{customer_id}")
    assert get_response.json()["data"]["email"] == "new@example.com"


def test_update_customer_invalid_uuid(client):
    invalid_customer_id = "invalid-uuid"
    response = client.put(
        f"/customers/{invalid_customer_id}", json={"email": "test@example.com"}
    )

    assert response.status_code == 422
    assert "detail" in response.json()


def test_update_customer_not_found(client):
    non_existent_customer_id = str(uuid.uuid4())

    response = client.put(
        f"/customers/{non_existent_customer_id}", json={"email": "test@example.com"}
    )

    assert response.status_code == 404
    assert response.json()["message"] == "Customer not found"


def test_update_customer_empty_email(client):
    customer_response = client.post(
        "/customers", json={"email": "test@example.com", "password": "testpass123"}
    ).json()
    customer_id = customer_response["data"]["id"]

    response = client.put(f"/customers/{customer_id}", json={"email": ""})

    assert response.status_code == 400
    assert response.json()["message"] == "Invalid request body"


def test_update_customer_duplicate_email(client):
    client.post(
        "/customers", json={"email": "existing@example.com", "password": "testpass123"}
    )

    customer_2_response = client.post(
        "/customers", json={"email": "customer2@example.com", "password": "testpass123"}
    ).json()
    customer_2_id = customer_2_response["data"]["id"]

    response = client.put(
        f"/customers/{customer_2_id}", json={"email": "existing@example.com"}
    )

    assert response.status_code == 409
    assert response.json()["message"] == "Email already exists"


def test_update_customer_using_same_email(client):
    create_customer_response = client.post(
        "/customers", json={"email": "test@example.com", "password": "testpass123"}
    ).json()
    customer_id = create_customer_response["data"]["id"]

    response = client.put(
        f"/customers/{customer_id}", json={"email": "test@example.com"}
    )

    assert response.status_code == 409
    assert response.json()["message"] == "Email already exists"
