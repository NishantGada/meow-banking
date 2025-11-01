from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

# local imports
from config.dbconfig import get_db
from main import app
from models.customer import Customer


class CustomerCreate(BaseModel):
    email: str
    password: str


@app.get("/customers/{customer_id}")
def get_customer__by_customer_id(customer_id: str, db: Session = Depends(get_db)):
    customers = db.query(Customer).filter(Customer.id == customer_id).all()
    return {"customers": customers}


@app.post("/customers")
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    new_customer = Customer(email=customer.email, password=customer.password)
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    return {"id": new_customer.id, "email": new_customer.email}
