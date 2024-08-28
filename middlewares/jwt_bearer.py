from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer
from utilss.jwt_manager import validate_token

class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request):
        # Rutas públicas que no requieren autenticación
        public_routes = ["/usuarios/register", "/usuarios/login"]

        if request.url.path in public_routes:
            return

        # Para rutas protegidas, se requiere un token
        auth = await super().__call__(request)
        if not auth.credentials:
            raise HTTPException(status_code=401, detail="Token requerido")
        
        try:
            data = validate_token(auth.credentials)
        except Exception as e:
            raise HTTPException(status_code=401, detail=str(e))
