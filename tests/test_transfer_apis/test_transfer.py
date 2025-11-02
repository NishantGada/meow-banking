import uuid
from tests.test_transfer_apis.test_helpers import create_customer_with_account


def test_transfer_success(client):
    customer_id_1, account_id_1 = create_customer_with_account(
        client, "customer1@example.com", 1000.00
    )
    customer_id_2, account_id_2 = create_customer_with_account(
        client, "customer2@example.com", 500.00
    )

    response = client.post(
        "/transfer",
        json={
            "from_account_id": account_id_1,
            "to_account_id": account_id_2,
            "amount": 200.00,
        },
    )

    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["message"] == "Transfer successful"
    assert response.json()["data"]["amount"] == 200.00

    account_1 = client.get(f"/customers/{customer_id_1}/accounts/{account_id_1}").json()
    account_2 = client.get(f"/customers/{customer_id_2}/accounts/{account_id_2}").json()

    assert account_1["data"]["balance"] == 800.00
    assert account_2["data"]["balance"] == 700.00


def test_transfer_source_account_not_found(client):
    customer_id_2, account_id_2 = create_customer_with_account(
        client, "customer@example.com"
    )
    non_existent_account_id = str(uuid.uuid4())

    response = client.post(
        "/transfer",
        json={
            "from_account_id": non_existent_account_id,
            "to_account_id": account_id_2,
            "amount": 100.00,
        },
    )

    assert response.status_code == 404
    assert response.json()["success"] == False
    assert response.json()["message"] == "Source acount not found"


def test_transfer_destination_account_not_found(client):
    customer_id_1, account_id_1 = create_customer_with_account(
        client, "customer@example.com"
    )
    non_existent_account_id = str(uuid.uuid4())

    response = client.post(
        "/transfer",
        json={
            "from_account_id": account_id_1,
            "to_account_id": non_existent_account_id,
            "amount": 100.00,
        },
    )

    assert response.status_code == 404
    assert response.json()["success"] == False
    assert response.json()["message"] == "Destination acount not found"


def test_transfer_from_closed_account(client):
    customer_id_1, account_id_1 = create_customer_with_account(
        client, "customer1@example.com", 1000.00
    )
    customer_id_2, account_id_2 = create_customer_with_account(
        client, "customer2@example.com", 500.00
    )

    # withdrawing all money so that the balance in source account is now 0 - which will allow us to close this account
    account_1 = client.post(
        "/withdraw",
        json={"user_id": customer_id_1, "account_id": account_id_1, "amount": 1000.00},
    ).json()

    assert account_1["data"]["current_balance"] == 0.0
    close_account_response = client.put(f"/accounts/{account_id_1}/close").json()
    assert close_account_response["data"]["status"] == "closed"

    response = client.post(
        "/transfer",
        json={
            "from_account_id": account_id_1,
            "to_account_id": account_id_2,
            "amount": 100.00,
        },
    )

    assert response.status_code == 400
    assert response.json()["success"] == False
    assert response.json()["message"] == "Account is closed"


def test_transfer_invalid_amount(client):
    customer_id_1, account_id_1 = create_customer_with_account(
        client, "customer1@example.com"
    )
    customer_id_2, account_id_2 = create_customer_with_account(
        client, "customer2@example.com"
    )

    response = client.post(
        "/transfer",
        json={
            "from_account_id": account_id_1,
            "to_account_id": account_id_2,
            "amount": -50.00,
        },
    )

    assert response.status_code == 422
    assert "detail" in response.json()
    assert response.json()["detail"][0]["type"] == "greater_than"
