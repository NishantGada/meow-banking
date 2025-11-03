import uuid
from decimal import Decimal


def create_customer_with_account(client, email, initial_deposit=1000.00):
    create_customer_response = client.post(
        "/customers", json={"email": email, "password": "pass123"}
    ).json()
    customer_id = create_customer_response["data"]["id"]

    account_response = client.post(
        "/accounts",
        json={
            "customer_id": customer_id,
            "initial_deposit": initial_deposit,
            "account_type": "checking",
        },
    ).json()
    account_id = account_response["data"]["account_id"]

    return customer_id, account_id
