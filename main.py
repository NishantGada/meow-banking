from fastapi import FastAPI

# local imports
from config.dbconfig import engine, Base
from config.logging_config import setup_logging


app = FastAPI()
setup_logging()

Base.metadata.create_all(bind=engine)
import apis.customer
import apis.account


@app.get("/")
def home():
    return {"message": "Meow Banking API"}
