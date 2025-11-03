import uuid
from tests.test_helpers import create_customer_with_account


def test_update_account_success(client):
    customer_id, account_id = create_customer_with_account(client, "test@example.com")

    response = client.put(f"/accounts/{account_id}", json={"account_type": "savings"})

    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["data"]["account_type"] == "savings"


def test_update_account_same_type(client):
    customer_id, account_id = create_customer_with_account(client, "test@example.com")

    response = client.put(f"/accounts/{account_id}", json={"account_type": "checking"})

    assert response.status_code == 400
    assert response.json()["success"] == False
    assert "already" in response.json()["message"]


def test_update_account_not_found(client):
    non_existent_id = str(uuid.uuid4())

    response = client.put(
        f"/accounts/{non_existent_id}", json={"account_type": "savings"}
    )

    assert response.status_code == 404
    assert response.json()["success"] == False
    assert response.json()["message"] == "Account not found"


def test_update_closed_account(client):
    customer_id, account_id = create_customer_with_account(
        client, "test@example.com", 100.00
    )

    # withdrawing all money to bring account balance to 0
    client.post(
        "/withdraw",
        json={"user_id": customer_id, "account_id": account_id, "amount": 100.00},
    )

    client.put(f"/accounts/{account_id}/close")

    response = client.put(f"/accounts/{account_id}", json={"account_type": "savings"})

    assert response.status_code == 400
