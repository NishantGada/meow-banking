from fastapi import Depends
from sqlalchemy.orm import Session

# local imports
from apis.helper_functions.generate_account_number import generate_account_number
from apis.helper_functions.response import success_response, error_response
from apis.schemas import AccountCreate
from apis.transfer import deposit_money
from config.dbconfig import get_db
from main import app
from models.account import Account
from models.customer import Customer
from models.transaction import AccountTransactions


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
