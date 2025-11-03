from fastapi import Depends
from sqlalchemy.orm import Session
from decimal import Decimal

# local imports
from apis.helper_functions.account_helpers import (
    check_if_account_exists,
    validate_account_status,
)
from config.logging_config import log_error, log_info
from main import app
from apis.helper_functions.response import error_response, success_response
from apis.schemas import DepositSchema, TransferCreate, WithdrawSchema
from config.dbconfig import get_db
from models.account import Account
from models.transaction import AccountTransactions, TransactionTypeEnum


def deposit_money(account_id, amount, db, description=""):
    log_info(f"deposit_money:: depositing money for {account_id}", amount=float(amount))
    transaction = AccountTransactions(
        account_id=account_id,
        transaction_type="deposit",
        amount=amount,
        description=description,
    )
    db.add(transaction)
    db.commit()


def withdraw_money(account_id, amount, db):
    log_info(
        f"withdraw_money:: withdrawing money for {account_id}", amount=float(amount)
    )
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
    try:
        source_account = str(transfer.from_account_id)
        destination_account = str(transfer.to_account_id)

        from_account = db.query(Account).filter(Account.id == source_account).first()
        if not from_account:
            return error_response("Source acount not found", status_code=404)

        error = validate_account_status(from_account)
        if error:
            return error

        to_account = db.query(Account).filter(Account.id == destination_account).first()
        if not to_account:
            return error_response("Destination acount not found", status_code=404)

        error = validate_account_status(to_account)
        if error:
            return error

        if from_account.balance < transfer.amount:
            return error_response("Insufficient balance", status_code=400)

        transfer_money(source_account, destination_account, transfer.amount, db)

        return success_response(
            data={
                "from_account": source_account,
                "to_account": destination_account,
                "amount": transfer.amount,
            },
            message="Transfer successful",
            status_code=200,
        )
    except Exception as e:
        db.rollback()
        log_error(
            "transfer failed",
            from_account_id=source_account,
            to_account_id=destination_account,
            error=str(e),
        )
        return error_response("Internal server error", status_code=500)


@app.post("/withdraw")
def withdraw(request_body: WithdrawSchema, db: Session = Depends(get_db)):
    try:
        withdrawal_account = str(request_body.account_id)
        account, error = check_if_account_exists(withdrawal_account, db)
        if error:
            return error

        withdrawal_amount = Decimal(str(request_body.amount))

        if account.customer_id != str(request_body.user_id):
            return error_response("Incorrect account", status_code=400)

        if withdrawal_amount <= 0:
            return error_response("Incorrect amount value", status_code=400)

        if withdrawal_amount > account.balance:
            return error_response("Insufficient balance", status_code=400)

        account.balance -= withdrawal_amount

        withdraw_money(request_body.account_id, withdrawal_amount, db)

        return success_response(
            data={"current_balance": float(account.balance)},
            message="Withdrawal successful",
            status_code=200,
        )
    except Exception as e:
        db.rollback()
        log_error(
            "withdraw failed",
            customer_id=request_body.user_id,
            account_id=withdrawal_account,
            error=str(e),
        )
        return error_response("Internal server error", status_code=500)


@app.post("/deposit")
def deposit(request_body: DepositSchema, db: Session = Depends(get_db)):
    try:
        deposit_account = str(request_body.account_id)
        account, error = check_if_account_exists(deposit_account, db)
        if error:
            return error

        deposit_amount = Decimal(str(request_body.amount))

        if account.customer_id != str(request_body.user_id):
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
    except Exception as e:
        db.rollback()
        log_error(
            "deposit failed",
            customer_id=request_body.user_id,
            account_id=deposit_account,
            error=str(e),
        )
        return error_response("Internal server error", status_code=500)
