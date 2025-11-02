import uuid


def test_get_customer_account_by_account_id_success(client):
    test_email = "test@example.com"
    create_customer_response = client.post(
        "/customers", json={"email": test_email, "password": "testpass123"}
    ).json()

    customer = create_customer_response["data"]
    customer_id = customer["id"]

    account = client.post(
        "/accounts",
        json={
            "customer_id": customer_id,
            "initial_deposit": 1000.00,
            "account_type": "saving",
        },
    ).json()
    print("account: ", account)
    account_id = account["data"]["account_id"]

    response = client.get(f"/customers/{customer_id}/accounts/{account_id}")

    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["data"]["account_id"] == account_id
    assert response.json()["data"]["balance"] == 1000.00


def test_get_customer_account_invalid_customer_uuid(client):
    invalid_customer_id = "invalid-uuid"
    valid_account_id = str(uuid.uuid4())

    response = client.get(
        f"/customers/{invalid_customer_id}/accounts/{valid_account_id}"
    )

    assert response.status_code == 422
    assert "detail" in response.json()


def test_get_customer_account_invalid_account_uuid(client):
    valid_customer_id = str(uuid.uuid4())
    invalid_account_id = "invalid-uuid"

    response = client.get(
        f"/customers/{valid_customer_id}/accounts/{invalid_account_id}"
    )

    assert response.status_code == 422
    assert "detail" in response.json()


def test_get_customer_account_customer_not_found(client):
    non_existent_customer_id = str(uuid.uuid4())
    valid_account_id = str(uuid.uuid4())

    response = client.get(
        f"/customers/{non_existent_customer_id}/accounts/{valid_account_id}"
    )

    assert response.status_code == 404
    assert response.json()["message"] == "Customer not found"


def test_get_customer_account_account_not_found(client):
    customer_response = client.post(
        "/customers", json={"email": "test@example.com", "password": "testpass123"}
    ).json()
    customer_id = customer_response["data"]["id"]

    non_existent_account_id = str(uuid.uuid4())

    response = client.get(
        f"/customers/{customer_id}/accounts/{non_existent_account_id}"
    )

    assert response.status_code == 404
    assert response.json()["message"] == "Account doesn't exist"


def test_get_customer_account_wrong_customer(client):
    customer_1_response = client.post(
        "/customers",
        json={"email": "customer_1@example.com", "password": "testpass123"},
    ).json()
    customer_1_id = customer_1_response["data"]["id"]

    # creating an account for the newly created customer_1
    create_account_response = client.post(
        "/accounts",
        json={
            "customer_id": customer_1_id,
            "initial_deposit": 1000.00,
            "account_type": "checking",
        },
    ).json()
    account_id = create_account_response["data"]["account_id"]

    # creating customer_2 to simulate invalid account access
    customer_2_response = client.post(
        "/customers",
        json={"email": "customer_2@example.com", "password": "testpass123"},
    ).json()
    customer_2_id = customer_2_response["data"]["id"]

    response = client.get(f"/customers/{customer_2_id}/accounts/{account_id}")

    assert response.status_code == 404
    assert response.json()["message"] == "Invalid account - try changing the account ID"
