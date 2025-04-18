from fastapi import APIRouter, Response, HTTPException
from ..schemas import UserSchemas

router = APIRouter(
    prefix="/users"
)


@router.post("/reset-password")
async def send_verification_user(
    response: Response,
    reset_password: UserSchemas.ResetPassword
    ):

    try:
        return {'message': 'Password reset successfully'}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))