from fastapi import Depends
from sqlalchemy.orm import Session

# local imports
from apis.helper_functions.generate_account_number import generate_account_number
from apis.helper_functions.response import success_response, error_response
from apis.helper_functions.validate_account_status import validate_account_status
from apis.schemas import AccountCreate, AccountUpdate
from apis.transfer import deposit_money
from config.dbconfig import get_db
from main import app
from models.account import Account, AccountStatusEnum
from models.customer import Customer
from models.transaction import AccountTransactions

"""
@app.get("/accounts/{customer_id}")
def get_all_customer_accounts(customer_id: str, db: Session = Depends(get_db)):
    accounts = db.query(Account).filter(Account.customer_id == customer_id).all()

    if not accounts:
        return success_response(
            data=[], message="No accounts to fetch", status_code=200
        )

    return success_response(
        data=[
            {
                "account_id": acc.id,
                "account_number": acc.account_number,
                "balance": float(acc.balance),
                "account_type": acc.account_type,
            }
            for acc in accounts
        ],
        message="Successfully fetched all customer accounts",
        status_code=200,
    )
"""


@app.get("/accounts/{account_id}")
def get_account_by_account_id(account_id: str, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()

    if not account:
        return error_response(data=[], message="Account not found", status_code=404)

    return success_response(
        data={
            "account_id": account.id,
            "account_number": account.account_number,
            "balance": float(account.balance),
            "account_type": account.account_type,
            "status": account.status,
        },
        message="Successfully fetched all customer accounts",
        status_code=200,
    )


"""
@app.get("/accounts/{customer_id}/{account_id}")
def get_customer_account_by_account_id(
    customer_id: str, account_id: str, db: Session = Depends(get_db)
):
    account = (
        db.query(Account)
        .filter(Account.id == account_id, Account.customer_id == customer_id)
        .first()
    )

    if not account:
        return error_response(
            message="Account not found, re-check account ID", status_code=404
        )

    return success_response(
        data=account, message="Account details fetched successfully", status_code=200
    )
"""


@app.post("/accounts")
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == account.customer_id).first()
    if not customer:
        return error_response("Customer not found", status_code=404)

    new_account = Account(
        account_number=generate_account_number(),
        customer_id=account.customer_id,
        balance=account.initial_deposit,
        account_type=account.account_type,
    )
    db.add(new_account)
    db.flush()

    deposit_money(new_account.id, account.initial_deposit, "Initial deposit", db)

    return success_response(
        data={
            "account_id": new_account.id,
            "account_number": new_account.account_number,
            "balance": float(new_account.balance),
        },
        message="Account created successfully",
        status_code=201,
    )


@app.get("/accounts/{account_id}/transactions")
def get_account_transactions(account_id: str, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        return error_response("Account not found", status_code=404)
    account_balance = float(account.balance)

    transactions = (
        db.query(AccountTransactions)
        .filter(AccountTransactions.account_id == account_id)
        .order_by(AccountTransactions.created_at.desc())
        .all()
    )

    if not transactions:
        return success_response(data=[], message="No transactions found")

    history = [
        {
            "id": transaction.id,
            "transaction_type": transaction.transaction_type,
            "amount": float(transaction.amount),
            "description": transaction.description,
            "created_at": str(transaction.created_at),
        }
        for transaction in transactions
    ]

    return success_response(
        data={
            "current_balance": account_balance,
            "number_of_transactions": len(history),
            "history": history,
        },
        message="Transaction history fetched successfully",
    )


@app.put("/accounts/{account_id}")
def update_account(
    account_id: str, account_data: AccountUpdate, db: Session = Depends(get_db)
):
    if not account_data.account_type:
        return error_response("Account type required", status_code=400)

    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        return error_response("Account not found", status_code=404)

    error = validate_account_status(account)
    if error:
        return error

    account.account_type = account_data.account_type
    db.commit()

    return success_response(
        data={"account_id": account.id, "account_type": account.account_type},
        message="Account updated successfully",
    )


@app.put("/accounts/{account_id}/close")
def close_account(account_id: str, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        return error_response("Account not found", status_code=404)

    if account.status == AccountStatusEnum.CLOSED.value:
        return error_response("Account already closed", status_code=400)

    if account.balance != 0:
        return error_response(
            "Cannot close account with non-zero balance", status_code=400
        )

    account.status = AccountStatusEnum.CLOSED.value
    db.commit()

    return success_response(
        data={"account_id": account.id, "status": account.status},
        message="Account closed successfully",
    )


@app.put("/accounts/{account_id}/reactivate")
def reactivate_account(account_id: str, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        return error_response("Account not found", status_code=404)

    if account.status == AccountStatusEnum.ACTIVE.value:
        return error_response("Account already active", status_code=400)

    if account.balance != 0:
        return error_response(
            "Cannot re-activate account with non-zero balance", status_code=400
        )

    account.status = AccountStatusEnum.ACTIVE.value
    db.commit()

    return success_response(
        data={"account_id": account.id, "status": account.status},
        message="Account re-activated successfully",
    )
