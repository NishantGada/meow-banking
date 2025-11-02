from fastapi import Depends
from sqlalchemy.orm import Session
from decimal import Decimal

# local imports
from apis.helper_functions.account_helpers import validate_account_status
from config.logging_config import log_info
from main import app
from apis.helper_functions.response import error_response, success_response
from apis.schemas import DepositSchema, TransferCreate, WithdrawSchema
from config.dbconfig import get_db
from models.account import Account
from models.transaction import AccountTransactions, TransactionTypeEnum


def deposit_money(account_id, amount, db, description=""):
    log_info(f"deposit_money:: depositing money for {account_id}", amount=amount)
    transaction = AccountTransactions(
        account_id=account_id,
        transaction_type="deposit",
        amount=amount,
        description=description,
    )
    db.add(transaction)
    db.commit()


def withdraw_money(account_id, amount, db):
    log_info(f"withdraw_money:: withdrawing money for {account_id}", amount=amount)
    transaction = AccountTransactions(
        account_id=account_id,
        transaction_type="withdraw",
        amount=-amount,
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


@app.post("/withdraw")
def withdraw(request_body: WithdrawSchema, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == request_body.account_id).first()
    withdrawal_amount = Decimal(str(request_body.amount))

    if account.customer_id != request_body.user_id:
        return error_response("Incorrect account", status_code=400)

    if withdrawal_amount <= 0:
        return error_response("Incorrect amount value", status_code=400)

    if withdrawal_amount > account.balance:
        return error_response("Insufficient balance", status_code=400)

    account.balance -= withdrawal_amount

    withdraw_money(request_body.account_id, withdrawal_amount, db)

    return success_response(
        data={"current_balance": float(account.balance)},
        message="Wuithdrawal successful",
        status_code=200,
    )


@app.post("/deposit")
def deposit(request_body: DepositSchema, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == request_body.account_id).first()
    deposit_amount = Decimal(str(request_body.amount))

    if account.customer_id != request_body.user_id:
        return error_response("Incorrect account", status_code=400)

    if deposit_amount <= 0:
        return error_response("Incorrect amount value", status_code=400)

    account.balance += deposit_amount

    deposit_money(request_body.account_id, deposit_amount, db)

    return success_response(
        data={"current_balance": float(account.balance)},
        message="Deposit successful",
        status_code=200,
    )
