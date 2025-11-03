import uuid
from tests.test_helpers import create_customer_with_account


def test_get_customer_account_by_account_id_success(client):
    customer_id, account_id = create_customer_with_account(
        client, "test@example.com", 1000.00
    )

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
    customer_1_id, account_id = create_customer_with_account(
        client, "customer1@example.com", 1000.00
    )

    customer_2_response = client.post(
        "/customers", json={"email": "customer2@example.com", "password": "testpass123"}
    ).json()
    customer_2_id = customer_2_response["data"]["id"]

    # Customer 2 tries to access Customer 1's account
    response = client.get(f"/customers/{customer_2_id}/accounts/{account_id}")

    assert response.status_code == 404
    assert response.json()["message"] == "Invalid account - try changing the account ID"
