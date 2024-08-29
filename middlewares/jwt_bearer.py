from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer
from middlewares.jwt_utils import verify_token as validate_token

class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request):
        public_routes = ["/usuarios/register", "/usuarios/login", "/"]

        if request.url.path in public_routes:
            return

        auth = await super().__call__(request)
        if not auth.credentials:
            raise HTTPException(status_code=401, detail="Token requerido")
        
        try:
            data = validate_token(auth.credentials)
            print(f"Validación del token exitosa: {data}")  # Para depurar
        except Exception as e:
            print(f"Error al validar token: {e}")  # Para depurar
            raise HTTPException(status_code=401, detail=str(e))
