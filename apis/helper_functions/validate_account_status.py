from apis.helper_functions.response import error_response


def validate_account_status(account):
    if account.status != "active":
        return error_response(
            f"Account is {account.status}",
            status_code=400,
        )
    return None
