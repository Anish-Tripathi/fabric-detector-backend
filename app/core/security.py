from fastapi import Security, HTTPException, status, Request
from fastapi.security.api_key import APIKeyHeader

from app.core.config import settings

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


async def verify_api_key(request: Request, api_key: str = Security(api_key_header)):
    # Skip API key check for OPTIONS preflight requests
    if request.method == "OPTIONS":
        return None
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
        )
    return api_key
