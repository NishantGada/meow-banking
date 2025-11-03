import uuid
from tests.test_helpers import create_customer_with_account


def test_reactivate_account_success(client):
    customer_id, account_id = create_customer_with_account(
        client, "test@example.com", 1000.00
    )

    client.post(
        "/withdraw",
        json={"user_id": customer_id, "account_id": account_id, "amount": 1000.00},
    )

    client.put(f"/accounts/{account_id}/close")

    response = client.put(f"/accounts/{account_id}/reactivate")

    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["data"]["status"] == "active"


def test_reactivate_account_already_active(client):
    customer_id, account_id = create_customer_with_account(client, "test@example.com")

    response = client.put(f"/accounts/{account_id}/reactivate")

    assert response.status_code == 400
    assert response.json()["message"] == "Account already active"


def test_reactivate_account_not_found(client):
    non_existent_id = str(uuid.uuid4())

    response = client.put(f"/accounts/{non_existent_id}/reactivate")

    assert response.status_code == 404
