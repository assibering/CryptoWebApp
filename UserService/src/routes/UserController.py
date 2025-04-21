from fastapi import APIRouter, Response, HTTPException, Depends
from src.schemas import UserSchemas
from src.dependencies import get_user_service
from src.service.UserService import UserService

router = APIRouter(
    prefix="/users"
)

@router.get("/")
async def reset_password(
    response: Response,
    email: str,
    user_service: UserService = Depends(get_user_service)):
    try:
        return await user_service.get_user(email=email)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
#TEMPORARY - Kafka will be used for this
@router.post("/create-user")
async def reset_password(
    response: Response,
    User_instance: UserSchemas.User,
    user_service: UserService = Depends(get_user_service)):
    try:
        return await user_service.create_user(
            UserSchemas.User(
                email=User_instance.email
            )
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/reset-password")
async def reset_password(
    response: Response,
    reset_password: UserSchemas.ResetPassword,
    user_service: UserService = Depends(get_user_service)):
    try:
        return await user_service.reset_password(
            email="dummy@email.com",
            reset_password=reset_password
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/deactivate-user")
async def reset_password(
    response: Response,
    email: str,
    user_service: UserService = Depends(get_user_service)):
    try:
        return await user_service.deactivate_user(
            email=email
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))