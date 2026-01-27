import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from app.core.security import bearer_scheme
from app.auth.tokens import decode_access_token
from app.utils.exceptions import AuthenticationError
logger = logging.getLogger("FastAPIApp")

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    try:
        logger.info(f"This is the user id: {credentials.credentials}")
        
        return await decode_access_token(credentials.credentials)
    except AuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
