from fastapi import Depends, HTTPException, status

from app.dependencies.auth import get_current_user
from app.utils.claims import extract_roles
from app.utils.exceptions import AuthorizationError


def require_role(role: str):
    def checker(user=Depends(get_current_user)):
        roles = extract_roles(user)

        if role not in roles:
            raise AuthorizationError()

        return user

    return checker
