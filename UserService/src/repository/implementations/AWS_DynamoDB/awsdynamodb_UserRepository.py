from botocore.exceptions import ClientError
from types_aiobotocore_dynamodb import DynamoDBClient
from src.repository.interfaces import interface_UserRepository
from src.schemas import UserSchemas
from src.exceptions import ResourceNotFoundException, BaseAppException, ResourceAlreadyExistsException
import logging
from .utils import *

logger = logging.getLogger(__name__)

class UserRepository(interface_UserRepository.UserRepository):

    def __init__(self, client: DynamoDBClient):
        """
        Initialize the DynamoDB repository.
        """
        
        # Initialize DynamoDB client
        self.client = client
        
        # You could also use a table name prefix from settings
        self.table_name = "users"

    async def get_user(self, email: str) -> UserSchemas.User:
        '''
        This function returns a User instance from the database.
        Or raises an exception if the user does not exist.
        '''
        try:
            response = await self.client.get_item(
                TableName=self.table_name,
                Key=await get_key(
                    pkey_name="email",
                    pkey_value=email
                )
            )

            if 'Item' not in response:
                logger.warning(f"User with email {email} not found")
                raise ResourceNotFoundException(f"User with email {email} not found")
            
            return await dynamodb_to_basemodel(
                basemodel=UserSchemas.User,
                dynamodb_data=response['Item'],
                include_empty_string_in_stringsets=False
            )
        
        except ResourceNotFoundException:
            raise

        except Exception as e:
            logger.exception(f"Error getting user: {str(e)}")
            raise BaseAppException(f"Internal database error: {str(e)}") from e

    async def create_user(self, User_instance: UserSchemas.User) -> UserSchemas.User:
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
                    basemodel=UserSchemas.User(
                        email=User_instance.email,
                        is_active=True if User_instance.is_active else False
                    )
                ),
                ConditionExpression="attribute_not_exists(email)"
            )

            return UserSchemas.User(
                email=User_instance.email,
                is_active=True if User_instance.is_active else False
            )
        
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                logger.warning(f"User with email {User_instance.email} already exists")
                raise ResourceAlreadyExistsException(f"User with email {User_instance.email} already exists")
            logger.exception(f"DynamoDB error: {str(e)}")
            raise BaseAppException(f"Internal database error: {str(e)}") from e

        except Exception as e:
            logger.exception(f"Internal database error: {str(e)}")
            raise BaseAppException(f"Internal database error: {str(e)}") from e

    async def update_user(self, User_instance: UserSchemas.User) -> UserSchemas.User:
        """
        This function updates a User instance using put_item with a condition.
        It ensures the user exists before proceeding with the update.
        It returns the updated User instance.
        """
        try:
            response = await self.client.put_item(
                TableName=self.table_name,
                Item=await basemodel_to_dynamodb(basemodel=User_instance),
                ConditionExpression="attribute_exists(email)"  # Ensures user exists
            )
            
            return UserSchemas.User(
                email=User_instance.email,
                is_active=User_instance.is_active
            )
            
        except self.client.exceptions.ConditionalCheckFailedException:
            # Raised when ConditionExpression fails (user does not exist)
            raise ResourceNotFoundException(f"User with email {User_instance.email} not found")
        except Exception as e:
            logger.exception(f"Internal database error: {str(e)}")
            raise BaseAppException(f"Internal database error: {str(e)}") from e

