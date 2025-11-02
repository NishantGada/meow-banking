import uuid


def test_update_customer_password_success(client):
    create_customer_response = client.post(
        "/customers", json={"email": "test@example.com", "password": "oldpass123"}
    ).json()
    customer_id = create_customer_response["data"]["id"]

    response = client.put(
        f"/customers/{customer_id}/password",
        json={"current_password": "oldpass123", "new_password": "newpass456"},
    )

    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["message"] == "Customer updated successfully"

    # Verifying new password works by trying to change old password again
    wrong_old_response = client.put(
        f"/customers/{customer_id}/password",
        json={
            "current_password": "oldpass123",
            "new_password": "anotherpass",
        },
    )
    assert wrong_old_response.status_code == 400


def test_update_customer_password_invalid_uuid(client):
    invalid_customer_id = "invalid-uuid"
    response = client.put(
        f"/customers/{invalid_customer_id}/password",
        json={"current_password": "oldpass", "new_password": "newpass"},
    )

    assert response.status_code == 422
    assert "detail" in response.json()


def test_update_customer_password_customer_not_found(client):
    non_existent_customer_id = str(uuid.uuid4())

    response = client.put(
        f"/customers/{non_existent_customer_id}/password",
        json={"current_password": "oldpass", "new_password": "newpass"},
    )

    assert response.status_code == 404
    assert response.json()["message"] == "Customer not found"


def test_update_customer_password_using_incorrect_current_password(client):
    create_customer_response = client.post(
        "/customers", json={"email": "test@example.com", "password": "correctpass"}
    ).json()
    customer_id = create_customer_response["data"]["id"]

    response = client.put(
        f"/customers/{customer_id}/password",
        json={"current_password": "wrongpass", "new_password": "newpass123"},
    )

    assert response.status_code == 400
    assert response.json()["message"] == "Incorrect password"


def test_update_customer_password_missing_current_password(client):
    create_customer_response = client.post(
        "/customers", json={"email": "test@example.com", "password": "pass123"}
    ).json()
    customer_id = create_customer_response["data"]["id"]

    response = client.put(
        f"/customers/{customer_id}/password", json={"new_password": "newpass123"}
    )

    assert response.status_code == 422
    assert "detail" in response.json()
    assert response.json()["detail"][0]["type"] == "missing"


def test_update_customer_password_missing_new_password(client):
    create_customer_response = client.post(
        "/customers", json={"email": "test@example.com", "password": "pass123"}
    ).json()
    customer_id = create_customer_response["data"]["id"]

    response = client.put(
        f"/customers/{customer_id}/password", json={"current_password": "pass123"}
    )

    assert response.status_code == 422
    assert "detail" in response.json()
    assert response.json()["detail"][0]["type"] == "missing"


def test_update_customer_password_extra_field(client):
    create_customer_response = client.post(
        "/customers",
        json={"email": "test@example.com", "password": "pass123"},
    ).json()
    customer_id = create_customer_response["data"]["id"]

    response = client.put(
        f"/customers/{customer_id}/password",
        json={
            "current_password": "oldpass123",
            "new_password": "newpass123",
            "name": "test",
        },
    )

    assert response.status_code == 422
    assert "detail" in response.json()
    assert response.json()["detail"][0]["type"] == "extra_forbidden"
