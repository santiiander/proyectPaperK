from fastapi import APIRouter, Depends
from middlewares.auth_utils import get_current_user

router = APIRouter()

@router.get("/protected")
async def protected_route(user: dict = Depends(get_current_user)):
    return {"message": "This is a protected route", "user": user}
