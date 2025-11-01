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
