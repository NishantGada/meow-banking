from fastapi import Depends
from sqlalchemy.orm import Session

# local imports
from apis.helper_functions.response import success_response, error_response
from apis.schemas import CustomerCreate
from config.dbconfig import get_db
from main import app
from models.customer import Customer


@app.get("/customers/{customer_id}")
def get_customer_by_customer_id(customer_id: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    return success_response(
        data={
            "id": customer.id,
            "email": customer.email,
            "created_at": str(customer.created_at),
        },
        message="Customer details fetched successfully",
        status_code=200,
    )


@app.post("/customers")
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    existing = db.query(Customer).filter(Customer.email == customer.email).first()
    if existing:
        return error_response("Email already exists", status_code=400)

    new_customer = Customer(email=customer.email, password=customer.password)
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    return success_response(
        data={"id": new_customer.id, "email": new_customer.email},
        message="Customer created successfully",
        status_code=201,
    )
