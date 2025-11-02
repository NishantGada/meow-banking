from pydantic import BaseModel


class CustomerCreate(BaseModel):
    email: str
    password: str


class CustomerUpdate(BaseModel):
    email: str | None = None
    password: str | None = None


class AccountCreate(BaseModel):
    customer_id: str
    initial_deposit: float
    account_type: str = "checking"


class AccountUpdate(BaseModel):
    account_type: str | None = None


class TransferCreate(BaseModel):
    from_account_id: str
    to_account_id: str
    amount: float
