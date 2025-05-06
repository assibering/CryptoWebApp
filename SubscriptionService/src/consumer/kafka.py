import asyncio
import json
import logging
from src.logging_config import setup_logging
from typing import Dict, List, Any
from aiokafka import AIOKafkaConsumer
from src.service.SubscriptionService import SubscriptionService
from src.exceptions import ResourceAlreadyExistsException, BaseAppException
from src.db.db_context import get_db_session_for_background
from src.db.factory import create_subscription_repository


# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = "kafka:29092"
KAFKA_TOPICS = ["userservice.user"]  # Multiple topics
KAFKA_CONSUMER_GROUP = "subscription_service_group"
KAFKA_AUTO_COMMIT = True
KAFKA_MAX_POLL_INTERVAL_MS = 300000  # 5 minutes
KAFKA_SESSION_TIMEOUT_MS = 30000  # 30 seconds

class EventHandler:
    """Base class for event handlers"""
    
    async def handle(self, payload: Dict[str, Any]) -> None:
        """Handle the event payload"""
        raise NotImplementedError("Subclasses must implement handle method")


class UserCreatedSuccessHandler(EventHandler):
    async def handle(
            self,
            payload: Dict[str, Any]
        ) -> None:

        from src.schemas import SubscriptionSchemas
        logger.info(f"Processing user_created_success event: {payload}")
        # Implement your create subscription logic here
        try:
            async for db_session in get_db_session_for_background():
                subscription_repository = create_subscription_repository(db_session)
                subscription_service = SubscriptionService(subscription_repository)
                
                await subscription_service.create_subscription(
                subscription_create = SubscriptionSchemas.CreateSubscription(
                    subscription_type = payload.get("subscription_type", "free_tier"),
                    email = payload.get("email")
                )
            )

        except ResourceAlreadyExistsException:
            raise
        except Exception as e:
            logger.exception(f"Error creating subscription: {str(e)}")
            raise BaseAppException(f"Error creating subscription: {str(e)}") from e
        

class UserCreatedFailedHandler(EventHandler):
    async def handle(self, payload: Dict[str, Any]) -> None:
        logger.info(f"Processing user_created_failed event: {payload}")
        # Implement your user update logic here

class KafkaEventManager:
    """Manages Kafka event consumption and routing to appropriate handlers"""
    
    def __init__(self):
        self.consumer = None
        self.tasks = []
        self.event_handlers: Dict[str, EventHandler] = {}
        
    def register_handler(self, event_type: str, handler: EventHandler) -> None:
        """Register a handler for a specific event type"""
        self.event_handlers[event_type] = handler
        logger.info(f"Registered handler for event type: {event_type}")
        
    async def start(self, topics: List[str], bootstrap_servers: str, group_id: str) -> None:
        self.consumer = AIOKafkaConsumer(
            *topics,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            enable_auto_commit=KAFKA_AUTO_COMMIT,
            max_poll_interval_ms=KAFKA_MAX_POLL_INTERVAL_MS,
            session_timeout_ms=KAFKA_SESSION_TIMEOUT_MS,
            auto_offset_reset="earliest"
        )
        
        await self.consumer.start()
        logger.info(f"Kafka consumer started for topics: {topics}")
        
        # Start multiple consumer tasks for parallel processing
        for i in range(3):  # Number of parallel consumers
            task = asyncio.create_task(self._consume(i))
            self.tasks.append(task)
            
    async def _consume(self, worker_id: int) -> None:
        """Consume messages from Kafka and route to handlers using async iteration"""
        logger.info(f"Starting consumer worker {worker_id}")
        try:
            # Using async iteration pattern - cleaner and handles continuous polling
            async for msg in self.consumer:
                try:
                    event = msg.value
                    topic = msg.topic
                    
                    # Extract event type and payload
                    # Adjust this based on your actual message structure
                    event_type = event.get("payload", {}).get("type")
                    payload = event.get("payload", {}).get("payload", {})
                    
                    logger.info(f"Worker {worker_id} received event from topic {topic}: {event_type}")
                    
                    # Route to appropriate handler
                    await self._process_event(event_type, json.loads(payload))
                    
                except Exception as e:
                    logger.error(f"Error processing message: {e}", exc_info=True)
                    # Consider implementing a dead-letter queue here
                    
        except asyncio.CancelledError:
            logger.info(f"Consumer worker {worker_id} cancelled")
        except Exception as e:
            logger.error(f"Consumer worker {worker_id} error: {e}", exc_info=True)
        finally:
            logger.info(f"Consumer worker {worker_id} shutting down")
                
    async def _process_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Process an event by routing to the appropriate handler"""
        handler = self.event_handlers.get(event_type)
        
        if handler:
            try:
                await handler.handle(payload)
            except Exception as e:
                logger.error(f"Error in handler for {event_type}: {e}", exc_info=True)
        else:
            logger.warning(f"No handler registered for event type: {event_type}")
            
    async def stop(self) -> None:
        """Stop the Kafka consumer gracefully"""
        logger.info("Stopping Kafka event manager...")
        
        # Cancel all consumer tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()
            
        # Wait for tasks to complete
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
            self.tasks = []
            
        # Stop the consumer
        if self.consumer:
            await self.consumer.stop()
            self.consumer = None
            
        logger.info("Kafka consumer stopped")


# Create event manager instance
event_manager = KafkaEventManager()


async def setup_kafka_handlers():
    """Initialize and start Kafka event handlers"""
    # Register event handlers
    event_manager.register_handler("user_created_success", UserCreatedSuccessHandler())
    event_manager.register_handler("user_created_failed", UserCreatedFailedHandler())
    
    # Start the Kafka consumer
    await event_manager.start(
        topics=KAFKA_TOPICS,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=KAFKA_CONSUMER_GROUP
    )
