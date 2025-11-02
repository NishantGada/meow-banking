from fastapi import Depends
from sqlalchemy.orm import Session
import uuid

# local imports
from apis.helper_functions.check_if_customer_exists import check_if_customer_exists
from apis.helper_functions.response import success_response, error_response
from apis.helper_functions.secure_password import hash_password, verify_password
from apis.schemas import CustomerCreate, CustomerUpdate, PasswordUpdate
from config.dbconfig import get_db
from config.logging_config import log_error
from main import app
from models.account import Account
from models.customer import Customer


@app.get("/customers/{customer_id}")
def get_customer_by_customer_id(customer_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        customer, error = check_if_customer_exists(str(customer_id), db)
        if error:
            return error

        return success_response(
            data={
                "id": customer.id,
                "email": customer.email,
                "created_at": str(customer.created_at),
            },
            message="Customer details fetched successfully",
            status_code=200,
        )
    except Exception as e:
        log_error(
            "get_customer_by_customer_id failed",
            customer_id=str(customer_id),
            error=str(e),
        )
        return error_response("Internal server error", status_code=500)


@app.get("/customers/{customer_id}/accounts/{account_id}")
def get_customer_account_by_account_id(
    customer_id: uuid.UUID, account_id: uuid.UUID, db: Session = Depends(get_db)
):
    try:
        customer, error = check_if_customer_exists(str(customer_id), db)
        if error:
            return error

        account = db.query(Account).filter(Account.id == str(account_id)).first()
        if not account:
            return error_response("Account doesn't exist", status_code=404)

        # checking if the account being accessed even belongs to this customer or not
        if account.customer_id != str(customer_id):
            return error_response(
                "Invalid account - try changing the account ID", status_code=404
            )

        return success_response(
            data={
                "account_id": account.id,
                "account_number": account.account_number,
                "balance": float(account.balance),
                "account_type": account.account_type,
                "status": account.status.value,
            },
            message="Customer account details fetched successfully",
            status_code=200,
        )
    except Exception as e:
        log_error(
            "get_customer_account_by_account_id failed",
            customer_id=str(customer_id),
            error=str(e),
        )
        return error_response("Internal server error", status_code=500)


@app.get("/customers")
def get_all_customers(db: Session = Depends(get_db)):
    try:
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
    except Exception as e:
        log_error("get_all_customers failed", error=str(e))
        return error_response("Internal server error", status_code=500)


@app.post("/customers")
def create_new_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    try:
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
    except Exception as e:
        db.rollback()
        log_error("create_new_customer failed", email=customer.email, error=str(e))
        return error_response("Failed to create customer", status_code=500)


@app.put("/customers/{customer_id}")
def update_customer(
    customer_id: uuid.UUID, customer_data: CustomerUpdate, db: Session = Depends(get_db)
):
    try:
        if not customer_data.email:
            return error_response("Invalid request body", status_code=400)

        customer, error = check_if_customer_exists(str(customer_id), db)
        if error:
            return error

        if customer_data.email:
            existing = (
                db.query(Customer)
                .filter(
                    Customer.email == customer_data.email, Customer.id != customer_id
                )
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
    except Exception as e:
        db.rollback()
        log_error("update_customer failed", customer_id=str(customer_id), error=str(e))
        return error_response("Internal server error", status_code=500)


@app.put("/customers/{customer_id}/password")
def update_customer_password(
    customer_id: uuid.UUID, request_body: PasswordUpdate, db: Session = Depends(get_db)
):
    try:
        customer, error = check_if_customer_exists(str(customer_id), db)
        if error:
            return error

        if not verify_password(request_body.current_password, customer.password):
            return error_response("Incorrect password", status_code=400)
        customer.password = hash_password(request_body.new_password)

        db.commit()

        return success_response(
            data={"id": customer.id, "email": customer.email},
            message="Customer updated successfully",
        )
    except Exception as e:
        db.rollback()
        log_error(
            "update_customer_password failed",
            customer_id=str(customer_id),
            error=str(e),
        )
        return error_response("Internal server error", status_code=500)


@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        customer, error = check_if_customer_exists(str(customer_id), db)
        if error:
            return error

        # Checking if the customer has any accounts
        accounts = db.query(Account).filter(Account.customer_id == customer_id).first()
        if accounts:
            return error_response(
                "Cannnot delete customer with existing accounts", status_code=400
            )

        db.delete(customer)
        db.commit()

        return success_response(data=None, message="Customer deleted successfully")
    except Exception as e:
        db.rollback()
        log_error("delete_customer failed", customer_id=str(customer_id), error=str(e))
        return error_response("Internal server error", status_code=500)
