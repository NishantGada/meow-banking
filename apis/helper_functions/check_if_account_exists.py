from apis.helper_functions.response import error_response
from models.account import Account


def check_if_account_exists(account_id, db):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        return None, error_response("Account not found", status_code=404)
    return account, None
