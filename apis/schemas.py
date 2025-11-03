from pydantic import BaseModel, Field, EmailStr
from uuid import UUID

# local imports
from models.account import AccountTypeEnum


class CustomerCreate(BaseModel):
    email: EmailStr
    password: str

    class Config:
        extra = "forbid"


class CustomerUpdate(BaseModel):
    email: EmailStr | None = None

    class Config:
        extra = "forbid"


class AccountCreate(BaseModel):
    customer_id: UUID
    initial_deposit: float = Field(gt=0)
    account_type: AccountTypeEnum

    class Config:
        extra = "forbid"


class AccountUpdate(BaseModel):
    account_type: AccountTypeEnum | None = None

    class Config:
        extra = "forbid"


class TransferCreate(BaseModel):
    from_account_id: UUID
    to_account_id: UUID
    amount: float = Field(gt=0)

    class Config:
        extra = "forbid"


class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

    class Config:
        extra = "forbid"


class WithdrawSchema(BaseModel):
    user_id: UUID
    account_id: UUID
    amount: float = Field(gt=0)

    class Config:
        extra = "forbid"


class DepositSchema(BaseModel):
    user_id: UUID
    account_id: UUID
    amount: float = Field(gt=0)

    class Config:
        extra = "forbid"
