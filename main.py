from fastapi import FastAPI, Request
import time

# local imports
from config.dbconfig import engine, Base
from config.logging_config import log_error, log_info, log_warning, setup_logging


app = FastAPI()
setup_logging()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    log_info("request_started", method=request.method, path=request.url.path)

    response = await call_next(request)

    duration = time.time() - start_time
    log_data = {
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": round(duration * 1000, 2),
    }

    if response.status_code >= 500:
        log_error("request_completed", **log_data)
    elif response.status_code >= 400:
        log_warning("request_completed", **log_data)
    else:
        log_info("request_completed", **log_data)

    return response


Base.metadata.create_all(bind=engine)
import apis.customer
import apis.account


@app.get("/")
def home():
    return {"message": "Meow Banking API"}
