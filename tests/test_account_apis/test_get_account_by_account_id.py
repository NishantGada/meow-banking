import uuid
from tests.test_helpers import create_customer_with_account


def test_get_account_by_id_success(client):
    customer_id, account_id = create_customer_with_account(
        client, "test@example.com", 1500.00
    )

    response = client.get(f"/accounts/{account_id}")

    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["data"]["account_id"] == account_id
    assert response.json()["data"]["balance"] == 1500.00


def test_get_account_by_id_not_found(client):
    non_existent_id = str(uuid.uuid4())

    response = client.get(f"/accounts/{non_existent_id}")

    assert response.status_code == 404
    assert response.json()["success"] == False
    assert response.json()["message"] == "Account not found"


def test_get_account_by_id_invalid_uuid(client):
    response = client.get("/accounts/invalid-uuid")

    assert response.status_code == 422
    assert "detail" in response.json()
