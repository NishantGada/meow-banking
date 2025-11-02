from fastapi import Depends
from sqlalchemy.orm import Session

# local imports
from apis.helper_functions.response import success_response, error_response
from apis.helper_functions.secure_password import hash_password, verify_password
from apis.schemas import CustomerCreate, CustomerUpdate, PasswordUpdate
from config.dbconfig import get_db
from main import app
from models.account import Account
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


@app.get("/customers")
def get_all_customers(db: Session = Depends(get_db)):
    customers = db.query(Customer).all()

    all_customers = [
        {
            "id": customer.id,
            "email": customer.email,
            "password": customer.password,
            "created_at": str(customer.created_at),
            "updated_at": str(customer.updated_at),
        }
        for customer in customers
    ]

    return success_response(
        data={
            "number_of_customers": len(all_customers),
            "all_customers": all_customers,
        },
        message="All customers fetched successfully",
        status_code=200,
    )


@app.post("/customers")
def create_new_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    existing = db.query(Customer).filter(Customer.email == customer.email).first()
    if existing:
        return error_response("Email already exists", status_code=400)

    new_customer = Customer(
        email=customer.email, password=hash_password(customer.password)
    )

    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    return success_response(
        data={"id": new_customer.id, "email": new_customer.email},
        message="Customer created successfully",
        status_code=201,
    )


@app.put("/customers/{customer_id}")
def update_customer(
    customer_id: str, customer_data: CustomerUpdate, db: Session = Depends(get_db)
):
    if not customer_data.email:
        return error_response("Invalid request body", status_code=400)

    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return error_response("Customer not found", status_code=404)

    if customer_data.email:
        existing = (
            db.query(Customer)
            .filter(Customer.email == customer_data.email, Customer.id != customer_id)
            .first()
        )
        if existing:
            return error_response("Email already exists", status_code=409)
        customer.email = customer_data.email

    db.commit()

    return success_response(
        data={"id": customer.id, "email": customer.email},
        message="Password updated successfully",
    )


@app.put("/customers/{customer_id}/password")
def update_customer_password(
    customer_id: str, request_body: PasswordUpdate, db: Session = Depends(get_db)
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return error_response("Customer not found", status_code=400)

    if not verify_password(request_body.current_password, customer.password):
        return error_response("Incorrect password", status_code=400)
    customer.password = hash_password(request_body.new_password)

    db.commit()

    return success_response(
        data={"id": customer.id, "email": customer.email},
        message="Customer updated successfully",
    )


@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return error_response("Customer not found", status_code=404)

    # Checking if the customer has any accounts
    accounts = db.query(Account).filter(Account.customer_id == customer_id).first()
    if accounts:
        return error_response(
            "Cannnot delete customer with existing accounts", status_code=400
        )

    db.delete(customer)
    db.commit()

    return success_response(data=None, message="Customer deleted successfully")
