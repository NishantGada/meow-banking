from pydantic import BaseModel


class CustomerCreate(BaseModel):
    email: str
    password: str