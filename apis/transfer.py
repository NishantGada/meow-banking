from fastapi import Depends
from sqlalchemy.orm import Session
from decimal import Decimal

# local imports
from apis.helper_functions.validate_account_status import validate_account_status
from main import app
from apis.helper_functions.response import error_response, success_response
from apis.schemas import TransferCreate
from config.dbconfig import get_db
from models.account import Account
from models.transaction import AccountTransactions


def deposit_money(account_id, amount, description, db):
    transaction = AccountTransactions(
        account_id=account_id,
        transaction_type="deposit",
        amount=amount,
        description=description,
    )
    db.add(transaction)
    db.commit()


def transfer_money(from_account_id, to_account_id, amount, db):
    amount = Decimal(str(amount))

    # this code updates balances in both - the source and destination accounts
    from_account = db.query(Account).filter(Account.id == from_account_id).first()
    to_account = db.query(Account).filter(Account.id == to_account_id).first()

    from_account.balance -= amount
    to_account.balance += amount

    # this code creates the transaction records for both - the source and destination accounts
    debit_transaction = AccountTransactions(
        account_id=from_account_id,
        transaction_type="transfer",
        amount=-amount,
        to_account_id=to_account_id,
        description=f"Transfer to account {to_account_id}",
    )
    db.add(debit_transaction)

    credit_transaction = AccountTransactions(
        account_id=to_account_id,
        transaction_type="transfer",
        amount=amount,
        from_account_id=from_account_id,
        description=f"Transfer from account {from_account_id}",
    )
    db.add(credit_transaction)

    db.commit()


@app.post("/transfer")
def transfer(transfer: TransferCreate, db: Session = Depends(get_db)):
    from_account = (
        db.query(Account).filter(Account.id == transfer.from_account_id).first()
    )
    if not from_account:
        return error_response("Source acount not found", status_code=404)

    error = validate_account_status(from_account)
    if error:
        return error

    to_account = db.query(Account).filter(Account.id == transfer.to_account_id).first()
    if not to_account:
        return error_response("Destination acount not found", status_code=404)

    error = validate_account_status(to_account)
    if error:
        return error

    if from_account.balance < transfer.amount:
        return error_response("Insufficient balance", status_code=400)

    transfer_money(
        transfer.from_account_id, transfer.to_account_id, transfer.amount, db
    )

    return success_response(
        data={
            "from_account": transfer.from_account_id,
            "to_account": transfer.to_account_id,
            "amount": transfer.amount,
        },
        message="Transfer successful",
        status_code=200,
    )
