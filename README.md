# Meow Banking API

A production-grade RESTful backend for a banking system built with Python, FastAPI and MySQL. Features include customer management, multi-account support, and secure money transfers.

## Features

- **Customer Management**: Create, Read, Update, and Delete customer accounts
- **Multi-Account Support**: Customers can have multiple bank accounts (checking/savings)
- **Transactions**: Deposits, withdrawals, and transfers between accounts, and between different customers
- **Account Management**: Close and Reactivate accounts
- **Security**: Password hashing with bcrypt and usage of UUID-based IDs
- **Logging**: Structured JSON logging with different log levels - INFO, WARNING, ERROR
- **Testing**: Unit and integration tests
- **Validation**: Request validation with Pydantic schemas

## Tech Stack

- **Framework**: FastAPI
- **Database**: MySQL
- **ORM**: SQLAlchemy
- **Authentication**: Bcrypt for password hashing
- **Testing**: Pytest
- **Validation**: Pydantic
- **Logging**: Python logging with JSON formatting
- **Language**: Python

## Installation & Setup

### Prerequisites

- Python
- MySQL
- pip

### 1. Clone the repository
```bash
git clone git@github.com:NishantGada/meow-banking.git
cd meow
```

### 2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the root directory:
```env
DB_USER=
PASSWORD=
DATABASE=
TEST_DATABASE=
```

### 5. Run the application
```bash
uvicorn main:app --reload
```

## API Documentation

Ensure the server is running, then visit:
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Testing

### Current Test Coverage ~ 91%

### Run all tests
```bash
pytest
```

### Run specific test file (example)
```bash
pytest tests/test_customer_apis/test_get_all_customers.py
```

### Run with coverage
```bash
pytest --cov=. tests/
```

### Generate HTML coverage report
```bash
pytest --cov=. --cov-report=html tests/
open htmlcov/index.html
```


## Potential Future Enhancements

- JWT authentication and authorization
- Set rules for creating a password
- Instead of deleting a customer, manage customer status as Active/Inactive
