import uuid
from tests.test_helpers import create_customer_with_account


def test_close_account_success(client):
    customer_id, account_id = create_customer_with_account(
        client, "test@example.com", 1000.00
    )

    client.post(
        "/withdraw",
        json={"user_id": customer_id, "account_id": account_id, "amount": 1000.00},
    )

    response = client.put(f"/accounts/{account_id}/close")

    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["data"]["status"] == "closed"


def test_close_account_already_closed(client):
    customer_id, account_id = create_customer_with_account(
        client, "test@example.com", 1000.00
    )

    client.post(
        "/withdraw",
        json={"user_id": customer_id, "account_id": account_id, "amount": 1000.00},
    )

    client.put(f"/accounts/{account_id}/close")

    # Trying to close the same account, again
    response = client.put(f"/accounts/{account_id}/close")

    assert response.status_code == 400
    assert response.json()["success"] == False
    assert response.json()["message"] == "Account already closed"


def test_close_account_non_zero_balance(client):
    customer_id, account_id = create_customer_with_account(
        client, "test@example.com", 1000.00
    )

    response = client.put(f"/accounts/{account_id}/close")

    assert response.status_code == 400
    assert response.json()["success"] == False
    assert response.json()["message"] == "Cannot close account with non-zero balance"


def test_close_account_not_found(client):
    non_existent_id = str(uuid.uuid4())

    response = client.put(f"/accounts/{non_existent_id}/close")

    assert response.status_code == 404
