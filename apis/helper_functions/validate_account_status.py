from apis.helper_functions.response import error_response


def validate_account_status(account):
    if account.status.value != "active":
        return error_response(
            f"Account is {account.status.value}",
            status_code=400,
        )
    return None
