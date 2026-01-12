from app.utils.constants import COGNITO_GROUPS_CLAIM

def extract_roles(payload: dict) -> list[str]:
    return payload.get(COGNITO_GROUPS_CLAIM, [])
