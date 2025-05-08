from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import SubscriptionController
from .exceptions import BaseAppException
import logging
from src.logging_config import setup_logging
from fastapi.responses import JSONResponse
from src.middleware.correlation_id_middleware import CorrelationIdMiddleware
from contextlib import asynccontextmanager
from src.db.settings import get_settings, DatabaseType
import aioboto3
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import httpx
from src.repository.implementations.PostgreSQL.debezium_config import generate_config_dict
from aiokafka import AIOKafkaConsumer
import json
import asyncio
from src.consumer.kafka import event_manager, setup_kafka_handlers

setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code (runs before application startup)
    # This is where you put code that was previously in @app.on_event("startup")
    logger.info("Running startup tasks...")

    #SOME STARTUP TASKS
    # Initialize settings
    settings = get_settings()
    if settings.DATABASE_TYPE == DatabaseType.POSTGRES:
        # Create an async engine
        engine = create_async_engine(settings.POSTGRES_DATABASE_URL, echo=True, future=True)

        # Create an async sessionmaker factory
        app.state.postgres_session = async_sessionmaker(
            bind=engine,
            expire_on_commit=False,  # optional: objects stay active after commit
            class_=AsyncSession
        )

        # Create Debezium connector
        connector_config = await generate_config_dict(
            settings=settings
        )
        async with httpx.AsyncClient() as client:
            resp = await client.post(settings.DEBEZIUM_URL, json=connector_config)
            if resp.status_code not in {201, 409}: # Created (201) or Already Exists (409)
                raise RuntimeError(f"Failed to register Debezium connector: {resp.status_code} {resp.text}")
        
    # Create the aioboto3 session at application startup if using DynamoDB
    elif settings.DATABASE_TYPE == DatabaseType.DYNAMODB:
        logger.info("Initializing DynamoDB session")
        app.state.dynamodb_session = aioboto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )

    # Start Kafka consumer as a background task
    await setup_kafka_handlers()

    logger.info("Startup tasks completed")
    yield
    # Shutdown code (runs after application shutdown)
    logger.info("Running shutdown tasks...")

    #SOME SHUTDOWN TASKS
    
    # Shutdown: stop Kafka consumer gracefully
    logger.info("Stopping Kafka consumer...")
    await event_manager.stop()

    logger.info("Shutdown tasks completed")
    # This is where you put code that was previously in @app.on_event("shutdown")

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST, GET, PUT"],
    allow_headers=["Authorization", "Content-Type"]
)

# Enable Correlation ID middleware
app.add_middleware(CorrelationIdMiddleware)

# Global exception handler
@app.exception_handler(BaseAppException)
async def app_exception_handler(request, exc):
    logger.error("Application error: %s", exc.message)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message}
    )


app.include_router(SubscriptionController.router)
    