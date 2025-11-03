import uuid
from tests.test_helpers import create_customer_with_account


def test_withdraw_success(client):
    customer_id, account_id = create_customer_with_account(
        client, "test@example.com", 1000.00
    )

    response = client.post(
        "/withdraw",
        json={"user_id": customer_id, "account_id": account_id, "amount": 300.00},
    )

    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["message"] == "Withdrawal successful"
    assert response.json()["data"]["current_balance"] == 700.00


def test_withdraw_insufficient_balance(client):
    customer_id, account_id = create_customer_with_account(
        client, "test@example.com", 500.00
    )

    response = client.post(
        "/withdraw",
        json={"user_id": customer_id, "account_id": account_id, "amount": 800.00},
    )

    assert response.status_code == 400
    assert response.json()["success"] == False
    assert response.json()["message"] == "Insufficient balance"


def test_withdraw_negative_amount(client):
    customer_id, account_id = create_customer_with_account(
        client, "test@example.com", 500.00
    )

    response = client.post(
        "/withdraw",
        json={"user_id": customer_id, "account_id": account_id, "amount": -100.00},
    )

    assert response.status_code == 422
    assert "detail" in response.json()
    assert response.json()["detail"][0]["type"] == "greater_than"


def test_withdraw_zero_amount(client):
    customer_id, account_id = create_customer_with_account(
        client, "test@example.com", 500.00
    )

    response = client.post(
        "/withdraw",
        json={"user_id": customer_id, "account_id": account_id, "amount": 0.0},
    )

    assert response.status_code == 422
    assert "detail" in response.json()
    assert response.json()["detail"][0]["type"] == "greater_than"


def test_withdraw_with_non_existent_account(client):
    customer_id, account_id = create_customer_with_account(
        client, "test@example.com", 500.00
    )

    non_existent_account_id = str(uuid.uuid4())

    response = client.post(
        "/withdraw",
        json={
            "user_id": customer_id,
            "account_id": non_existent_account_id,
            "amount": 100.00,
        },
    )

    assert response.status_code == 404
    assert response.json()["success"] == False
    assert response.json()["message"] == "Account not found"


def test_withdraw_with_incorrect_account(client):
    customer_id_1, account_id_1 = create_customer_with_account(
        client, "test_1@example.com", 500.00
    )
    customer_id_2, account_id_2 = create_customer_with_account(
        client, "test_2@example.com", 1000.00
    )

    # customer 1 is trying to withdraw money from a different customer's account
    response = client.post(
        "/withdraw",
        json={
            "user_id": customer_id_1,
            "account_id": account_id_2,
            "amount": 100.00,
        },
    )

    print("response.json(): ", response.json())

    assert response.status_code == 400
    assert response.json()["success"] == False
    assert response.json()["message"] == "Incorrect account"
