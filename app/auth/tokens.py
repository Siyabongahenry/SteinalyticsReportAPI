from jose import jwt
from auth.jwks import get_jwks
from app.core.OIDC_config import OIDC_ISSUER, OIDC_AUDIENCE, OIDC_ALGORITHMS
from utils.exceptions import AuthenticationError


async def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            await get_jwks(),
            algorithms=OIDC_ALGORITHMS,
            audience=OIDC_AUDIENCE,
            issuer=OIDC_ISSUER,
        )
    except Exception:
        raise AuthenticationError("Token validation failed")
