def test_get_all_customers_success(client):
    response = client.get("/customers")
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert "data" in response.json()
    assert "number_of_customers" in response.json()["data"]
    assert "all_customers" in response.json()["data"]
    assert type(response.json()["data"]["all_customers"]) == list
    # assert response.json()["data"]["email"] == "test@example.com"
