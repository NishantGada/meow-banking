import uuid


def test_create_account_success(client):
    customer_response = client.post(
        "/customers", json={"email": "test@example.com", "password": "pass123"}
    ).json()
    customer_id = customer_response["data"]["id"]

    response = client.post(
        "/accounts",
        json={
            "customer_id": customer_id,
            "initial_deposit": 2500.00,
            "account_type": "savings",
        },
    )

    assert response.status_code == 201
    assert response.json()["success"] == True
    assert response.json()["data"]["balance"] == 2500.00
    assert "account_id" in response.json()["data"]
    assert "account_number" in response.json()["data"]


def test_create_account_customer_not_found(client):
    non_existent_id = str(uuid.uuid4())

    response = client.post(
        "/accounts",
        json={
            "customer_id": non_existent_id,
            "initial_deposit": 1000.00,
            "account_type": "checking",
        },
    )

    assert response.status_code == 404
    assert response.json()["success"] == False
    assert response.json()["message"] == "Customer not found"


def test_create_account_negative_deposit(client):
    customer_response = client.post(
        "/customers", json={"email": "test@example.com", "password": "pass123"}
    ).json()
    customer_id = customer_response["data"]["id"]

    response = client.post(
        "/accounts",
        json={
            "customer_id": customer_id,
            "initial_deposit": -500.00,
            "account_type": "checking",
        },
    )

    assert response.status_code == 422
    assert "detail" in response.json()
    assert response.json()["detail"][0]["type"] == "greater_than"


def test_create_account_zero_deposit(client):
    customer_response = client.post(
        "/customers", json={"email": "test@example.com", "password": "pass123"}
    ).json()
    customer_id = customer_response["data"]["id"]

    response = client.post(
        "/accounts",
        json={
            "customer_id": customer_id,
            "initial_deposit": 0.00,
            "account_type": "checking",
        },
    )

    assert response.status_code == 422
    assert "detail" in response.json()
    assert response.json()["detail"][0]["type"] == "greater_than"
