from fastapi import Depends
from sqlalchemy.orm import Session

from apis.helper_functions.response import success_response, error_response
from apis.schemas import AccountCreate
from config.dbconfig import get_db
from main import app
from models.account import Account
from models.customer import Customer


@app.get("/accounts/{customer_id}")
def get_all_customer_accounts(customer_id: str, db: Session = Depends(get_db)):
    accounts = db.query(Account).filter(Account.customer_id == customer_id).first()
    
    if not accounts:
        return success_response(
            data=[],
            message="No accounts to fetch",
            status_code=200
        )
    
    return success_response(
        data=accounts,
        message="Successfully fetched all customer accounts",
        status_code=200
    )


@app.get("/accounts/{customer_id}/{account_id}")
def get_customer_account_by_account_id(customer_id: str, account_id: str, db: Session = Depends(get_db)):
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.customer_id == customer_id
    ).first()

    if not account:
        return error_response(
            message="Account not found, re-check account ID",
            status_code=404
        )

    return success_response(
        data=account,
        message="Account details fetched successfully",
        status_code=200
    )
