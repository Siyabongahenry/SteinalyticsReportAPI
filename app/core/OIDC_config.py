from app.core.settings import settings

OIDC_ISSUER = settings.oidc_issuer
OIDC_AUDIENCE = settings.oidc_audience
OIDC_ALGORITHMS = ["RS256"]

JWKS_URL = f"{OIDC_ISSUER}/.well-known/jwks.json"
