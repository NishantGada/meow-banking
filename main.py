from fastapi import FastAPI

# local imports
from config.dbconfig import engine, Base


app = FastAPI()
Base.metadata.create_all(bind=engine)
import apis.customer
import apis.account


@app.get("/")
def home():
    return {"message": "Meow Banking API"}
