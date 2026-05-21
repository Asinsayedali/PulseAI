from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from jose import JWTError
from app.utils.redis_client import redis_client
from app.core.security import decode_token

# Routes that skip JWT validation
PUBLIC_PATHS = {
    "/api/v1/auth/signup",
    "/api/v1/auth/login",
    "/",
    "/docs",
    "/openapi.json",
    "/redoc",
}


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"error": "Missing or invalid Authorization header"})

        token = auth_header.split(" ", 1)[1]
        try:
            payload = decode_token(token)
            if redis_client.get(f"blacklist:{token}"):
                return JSONResponse(status_code=401, content={"error": "Token has been revoked"})
            request.state.user_id = payload["sub"]
        except JWTError:
            return JSONResponse(status_code=401, content={"error": "Invalid or expired token"})

        return await call_next(request)
