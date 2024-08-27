from fastapi import Header, HTTPException, Depends
from middlewares.jwt_utils import verify_token

def get_current_user(authorization: str = Header(...)):
    token = authorization.split(" ")[1]  # Asume que el header es de tipo "Bearer <token>"
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload
