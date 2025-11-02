from apis.helper_functions.response import error_response
from models.customer import Customer


def check_if_customer_exists(customer_id, db):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return None, error_response("Customer not found", status_code=404)
    return customer, None
