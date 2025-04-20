from fastapi import APIRouter, Response, HTTPException, Depends
from src.schemas import UserSchemas
from src.dependencies import get_user_service
from src.service.UserService import UserService

router = APIRouter(
    prefix="/users"
)

#ONLY FOR DEBUGGING
@router.get("/get-table")
async def get_table(
    response: Response,
    user_service: UserService = Depends(get_user_service)):
    try:
        return await user_service.get_table()
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
        return await user_service.update_user(
            UserSchemas.User(
                email="dummy@email.com"
            )
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))