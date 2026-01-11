import httpx
from app.core.OIDC_config import JWKS_URL

_jwks_cache = None

async def get_jwks():
    global _jwks_cache

    if _jwks_cache is None:
        async with httpx.AsyncClient() as client:
            resp = await client.get(JWKS_URL)
            resp.raise_for_status()
            _jwks_cache = resp.json()

    return _jwks_cache
