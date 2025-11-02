def test_create_customer_success(client):
    response = client.post(
        "/customers", json={"email": "test@example.com", "password": "testpass123"}
    )
    assert response.status_code == 201
    assert response.json()["success"] == True
    assert "id" in response.json()["data"]
    assert response.json()["data"]["email"] == "test@example.com"


def test_create_customer_duplicate_email(client):
    response = client.post(
        "/customers", json={"email": "test@example.com", "password": "testpass123"}
    )
    response = client.post(
        "/customers", json={"email": "test@example.com", "password": "testpass123"}
    )
    assert response.status_code == 400
    assert response.json()["success"] == False
    assert response.json()["message"] == "Email already exists"


def test_create_customer_missing_email(client):
    response = client.post("/customers", json={"password": "testpass123"})
    assert response.status_code == 422
    assert "detail" in response.json()
    assert "email" in str(response.json()["detail"])
    assert response.json()["detail"][0]["type"] == "missing"


def test_create_customer_missing_password(client):
    response = client.post("/customers", json={"email": "test@example.com"})
    assert response.status_code == 422
    assert "detail" in response.json()
    assert "password" in str(response.json()["detail"])
    assert response.json()["detail"][0]["type"] == "missing"


def test_create_customer_invalid_request_field(client):
    response = client.post(
        "/customers",
        json={"email": "test@example.com", "password": "testpass123", "name": "test"},
    )
    assert response.status_code == 422
    assert "detail" in response.json()
    assert response.json()["detail"][0]["type"] == "extra_forbidden"

