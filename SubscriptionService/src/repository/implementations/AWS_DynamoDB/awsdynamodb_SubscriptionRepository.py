from botocore.exceptions import ClientError
from types_aiobotocore_dynamodb import DynamoDBClient
from src.repository.interfaces import interface_SubscriptionRepository
from src.schemas import SubscriptionSchemas
from src.exceptions import ResourceNotFoundException, BaseAppException, ResourceAlreadyExistsException
import logging
from .utils import *

logger = logging.getLogger(__name__)

class SubscriptionRepository(interface_SubscriptionRepository.SubscriptionRepository):

    def __init__(self, client: DynamoDBClient):
        """
        Initialize the DynamoDB repository.
        The db parameter is ignored (it's only here to maintain a consistent interface with PostgreSQL repository).
        """
        # Initialize DynamoDB client
        self.client = client
        
        # You could also use a table name prefix from settings
        self.table_name = "subscriptions"

    async def get_subscription(self, subscription_id: str) -> SubscriptionSchemas.Subscription:
        '''
        This function returns a User instance from the database.
        Or raises an exception if the user does not exist.
        '''
        try:
            response = await self.client.get_item(
                TableName=self.table_name,
                Key=await get_key(
                    pkey_name="subscription_id",
                    pkey_value=subscription_id
                )
            )

            if 'Item' not in response:
                logger.warning(f"Subscription with subscription_id {subscription_id} not found")
                raise ResourceNotFoundException(f"Subscription with subscription_id {subscription_id} not found")
            
            return await dynamodb_to_basemodel(
                basemodel=SubscriptionSchemas.Subscription,
                dynamodb_data=response['Item'],
                include_empty_string_in_stringsets=False
            )
        
        except ResourceNotFoundException:
            raise

        except Exception as e:
            logger.exception(f"Error getting subscription: {str(e)}")
            raise BaseAppException(f"Internal database error: {str(e)}") from e

    async def create_subscription(
            self,
            Subscription_instance: SubscriptionSchemas.Subscription
        ) -> SubscriptionSchemas.Subscription:
        '''
        This function inserts a User instance into the database.
        This function will not overwrite if the user already exists.
        It will raise an exception if the user already exists.
        This function will return the User instance.
        '''
        try:
            response = await self.client.put_item(
                TableName=self.table_name,
                Item=await basemodel_to_dynamodb(
                    basemodel=SubscriptionSchemas.Subscription(
                        subscription_id=Subscription_instance.subscription_id,
                        subscription_type=Subscription_instance.subscription_type,
                        email=Subscription_instance.email,
                        is_active=False if Subscription_instance.is_active == False else True #Default to True
                    )
                ),
                ConditionExpression="attribute_not_exists(subscription_id)"
            )

            return SubscriptionSchemas.Subscription(
                subscription_id=Subscription_instance.subscription_id,
                subscription_type=Subscription_instance.subscription_type,
                email=Subscription_instance.email,
                is_active=False if Subscription_instance.is_active else True #Default to True
            )
        
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                logger.warning(f"Subscription with subscription_id {Subscription_instance.subscription_id} already exists")
                raise ResourceAlreadyExistsException(f"Subscription with subscription_id {Subscription_instance.subscription_id} already exists")
            logger.exception(f"DynamoDB error: {str(e)}")
            raise BaseAppException(f"Internal database error: {str(e)}") from e

        except Exception as e:
            logger.exception(f"Internal database error: {str(e)}")
            raise BaseAppException(f"Internal database error: {str(e)}") from e