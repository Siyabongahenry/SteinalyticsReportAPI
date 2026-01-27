from fastapi import APIRouter, Depends
from app.dependencies.roles import require_role

router = APIRouter(prefix="/email-organizer",tags=["Email Organizer"])

@router.post("/groups")
async def get_groups(user=Depends(require_role("site-admin"))):

 return {
        "group": "Uploaded successfully"
     }