from fastapi import APIRouter, Depends
from src.schemas import UserSchemas
from src.dependencies import get_user_service
from src.service.UserService import UserService

router = APIRouter(
    prefix="/users"
)

@router.get("", status_code=200)
async def get_user(
    email: str,
    user_service: UserService = Depends(get_user_service)):
    return await user_service.get_user(email=email)
    
#TEMPORARY - Kafka will be used for this
@router.post("/create-user", status_code=201)
async def create_user(
    email: str,
    user_service: UserService = Depends(get_user_service)):
    return await user_service.create_user(email=email)

@router.put("/reset-password", status_code=201)
async def reset_password(
    email: str,
    #sessionId: str,
    reset_password: UserSchemas.ResetPassword,
    user_service: UserService = Depends(get_user_service)):

    # Check if sessionId is valid (sessionId == email in Redis or DB)
    # Will be implemented as Dependency Injection later

    return await user_service.reset_password(
        email=email,
        reset_password=reset_password
    )

@router.put("/deactivate-user", status_code=201)
async def deactivate_user(
    email: str,
    user_service: UserService = Depends(get_user_service)):
    return await user_service.deactivate_user(
        email=email
    )