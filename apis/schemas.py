import uuid
from pydantic import BaseModel
from uuid import UUID


class CustomerCreate(BaseModel):
    email: str
    password: str


class CustomerUpdate(BaseModel):
    email: str | None = None


class AccountCreate(BaseModel):
    customer_id: uuid.UUID
    initial_deposit: float
    account_type: str = "checking"


class AccountUpdate(BaseModel):
    account_type: str | None = None


class TransferCreate(BaseModel):
    from_account_id: str
    to_account_id: str
    amount: float


class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

    class Config:
        extra = "forbid"


class WithdrawSchema(BaseModel):
    # user_id: UUID
    user_id: str
    account_id: str
    amount: float


class DepositSchema(BaseModel):
    # user_id: UUID
    user_id: str
    account_id: str
    amount: float
