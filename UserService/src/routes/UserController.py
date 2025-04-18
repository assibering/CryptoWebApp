from fastapi import APIRouter, Response, HTTPException
from ..schemas import User

router = APIRouter(
    prefix="/users"
)


@router.post("/reset-password")
async def send_verification_user(
    response: Response,
    reset_password: User.ResetPassword
    ):

    try:
        return {'message': 'Password reset successfully'}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))