import uuid
from tests.test_helpers import create_customer_with_account


def test_get_account_transactions_success(client):
    customer_id, account_id = create_customer_with_account(
        client, "test@example.com", 1000.00
    )

    client.post(
        "/deposit",
        json={"user_id": customer_id, "account_id": account_id, "amount": 500.00},
    )
    client.post(
        "/withdraw",
        json={"user_id": customer_id, "account_id": account_id, "amount": 200.00},
    )

    response = client.get(f"/accounts/{account_id}/transactions")

    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["data"]["number_of_transactions"] == 3
    assert response.json()["data"]["current_balance"] == 1300.00


def test_get_account_transactions_account_not_found(client):
    non_existent_id = str(uuid.uuid4())

    response = client.get(f"/accounts/{non_existent_id}/transactions")

    assert response.status_code == 404
    assert response.json()["message"] == "Account not found"


def test_get_account_transactions_invalid_uuid(client):
    response = client.get("/accounts/invalid-uuid/transactions")

    assert response.status_code == 422
    assert "detail" in response.json()
    assert response.json()["detail"][0]["type"] == "uuid_parsing"
