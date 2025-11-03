import uuid
from tests.test_transfer_apis.test_helpers import create_customer_with_account


def test_deposit_success(client):
    customer_id, account_id = create_customer_with_account(
        client, "test@example.com", 1000.00
    )

    response = client.post(
        "/deposit",
        json={"user_id": customer_id, "account_id": account_id, "amount": 500.00},
    )

    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["message"] == "Deposit successful"
    assert response.json()["data"]["current_balance"] == 1500.00


def test_deposit_incorrect_account(client):
    customer_id_1, account_id_1 = create_customer_with_account(
        client, "customer1@example.com"
    )
    customer_id_2, account_id_2 = create_customer_with_account(
        client, "customer2@example.com"
    )

    # Customer 2 tries to deposit to Customer 1's account
    response = client.post(
        "/deposit",
        json={"user_id": customer_id_2, "account_id": account_id_1, "amount": 100.00},
    )

    assert response.status_code == 400
    assert response.json()["success"] == False
    assert response.json()["message"] == "Incorrect account"


def test_deposit_in_non_existent_account(client):
    customer_id, account_id = create_customer_with_account(
        client, "test@example.com", 500.00
    )

    non_existent_account_id = str(uuid.uuid4())

    response = client.post(
        "/deposit",
        json={
            "user_id": customer_id,
            "account_id": non_existent_account_id,
            "amount": 100.00,
        },
    )

    assert response.status_code == 404
    assert response.json()["success"] == False
    assert response.json()["message"] == "Account not found"


def test_deposit_negative_amount(client):
    customer_id, account_id = create_customer_with_account(client, "test@example.com")

    response = client.post(
        "/deposit",
        json={"user_id": customer_id, "account_id": account_id, "amount": -50.00},
    )

    assert response.status_code == 422
    assert "detail" in response.json()
    assert response.json()["detail"][0]["type"] == "greater_than"


def test_deposit_zero_amount(client):
    customer_id, account_id = create_customer_with_account(client, "test@example.com")

    response = client.post(
        "/deposit",
        json={"user_id": customer_id, "account_id": account_id, "amount": 0.00},
    )

    assert response.status_code == 422
    assert "detail" in response.json()
    assert response.json()["detail"][0]["type"] == "greater_than"
