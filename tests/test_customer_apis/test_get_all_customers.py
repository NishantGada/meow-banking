def test_get_all_customers_success(client):
    response = client.get("/customers")
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert "data" in response.json()
    assert "number_of_customers" in response.json()["data"]
    assert "all_customers" in response.json()["data"]
    assert type(response.json()["data"]["all_customers"]) == list


def test_get_all_customers_with_entries(client):
    client.post(
        "/customers", json={"email": "test_1@example.com", "password": "testpass123"}
    )
    client.post(
        "/customers", json={"email": "test_2@example.com", "password": "testpass123"}
    )
    client.post(
        "/customers", json={"email": "test_3@example.com", "password": "testpass123"}
    )

    response = client.get("/customers")

    assert response.status_code == 200
    assert (
        len(response.json()["data"]["all_customers"])
        == response.json()["data"]["number_of_customers"]
    )
    assert isinstance(response.json()["data"]["all_customers"][0], dict)
    assert len(response.json()["data"]["all_customers"][0]) == 4
