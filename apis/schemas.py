from pydantic import BaseModel


class CustomerCreate(BaseModel):
    email: str
    password: str


class AccountCreate(BaseModel):
    customer_id: str
    initial_deposit: float
    account_type: str = "checking"
