import random
import string

# local imports
from apis.helper_functions.response import error_response
from models.account import Account


def generate_account_number():
    return "".join(random.choices(string.digits, k=10))


def validate_account_status(account):
    if account.status.value != "active":
        return error_response(
            f"Account is {account.status.value}",
            status_code=400,
        )
    return None


def check_if_account_exists(account_id, db):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        return None, error_response("Account not found", status_code=404)
    return account, None
