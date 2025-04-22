from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import UserController
from .exceptions import BaseAppException
import logging
from src.logging_config import setup_logging
from fastapi.responses import JSONResponse
from src.middleware.correlation_id_middleware import CorrelationIdMiddleware

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI()

origins = [
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST, GET"],
    allow_headers=["Authorization", "Content-Type"]
)

# Enable Correlation ID middleware
app.add_middleware(CorrelationIdMiddleware)

# Define the startup method
@app.on_event("startup")
async def startup_event():
    # Call your method(s) to create tables or perform any startup tasks
    logger.info("Running startup tasks...")
    logger.info("Start up tasks completed")


# Global exception handler
@app.exception_handler(BaseAppException)
async def app_exception_handler(request, exc):
    logger.error("Application error: %s", exc.message)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message}
    )


app.include_router(UserController.router)
    