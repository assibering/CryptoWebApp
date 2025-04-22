from fastapi import APIRouter, Response, HTTPException, Depends
from src.schemas import UserSchemas
from src.dependencies import get_user_service
from src.service.UserService import UserService

router = APIRouter(
    prefix="/users"
)

@router.get("/")
async def get_user(
    response: Response,
    email: str,
    user_service: UserService = Depends(get_user_service)):
    return await user_service.get_user(email=email)
    
#TEMPORARY - Kafka will be used for this
@router.post("/create-user")
async def create_user(
    response: Response,
    User_instance: UserSchemas.User,
    user_service: UserService = Depends(get_user_service)):
    return await user_service.create_user(user_instance=User_instance)

@router.post("/reset-password")
async def reset_password(
    response: Response,
    reset_password: UserSchemas.ResetPassword,
    user_service: UserService = Depends(get_user_service)):
    return await user_service.reset_password(
        email="dummy@email.com",
        reset_password=reset_password
    )

@router.post("/deactivate-user")
async def deactivate_user(
    response: Response,
    email: str,
    user_service: UserService = Depends(get_user_service)):
    return await user_service.deactivate_user(
        email=email
    )