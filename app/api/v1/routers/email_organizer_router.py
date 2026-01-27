from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import io, csv
import pandas as pd  # for Excel support
from typing import List
from app.dependencies.roles import require_role
from app.services.email_organizer_service import EmailOrganizerService

router = APIRouter(prefix="/email-organizer", tags=["Email Organizer"])
service = EmailOrganizerService()

# =======================
# GROUPS
# =======================

@router.post("/groups")
async def create_group(
    group_id: str,
    name: str,
    managers: List[str] = [],
    user=Depends(require_role("site-admin"))
):
    return service.create_group(group_id, name, managers)

@router.get("/groups/{group_id}")
async def get_group(group_id: str, user=Depends(require_role("site-admin"))):
    group = service.get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group

@router.put("/groups/{group_id}")
async def update_group(group_id: str, updates: dict, user=Depends(require_role("site-admin"))):
    return service.update_group(group_id, updates)

@router.delete("/groups/{group_id}")
async def delete_group(group_id: str, user=Depends(require_role("site-admin"))):
    return service.delete_group(group_id)

# =======================
# RECIPIENTS
# =======================

@router.post("/groups/{group_id}/emails")
async def add_emails(group_id: str, emails: List[str], user=Depends(require_role("site-admin"))):
    return service.add_recipients(group_id, emails)

@router.put("/groups/{group_id}/emails")
async def replace_emails(group_id: str, emails: List[str], user=Depends(require_role("site-admin"))):
    return service.replace_recipients(group_id, emails)

@router.delete("/groups/{group_id}/emails/{email}")
async def remove_email(group_id: str, email: str, user=Depends(require_role("site-admin"))):
    return service.remove_recipient(group_id, email)

# =======================
# MANAGERS
# =======================

@router.post("/groups/{group_id}/managers")
async def add_manager(group_id: str, user_id: str, user=Depends(require_role("site-admin"))):
    return service.add_manager(group_id, user_id)

@router.delete("/groups/{group_id}/managers/{user_id}")
async def remove_manager(group_id: str, user_id: str, user=Depends(require_role("site-admin"))):
    return service.remove_manager(group_id, user_id)

# =======================
# LOGS
# =======================

@router.get("/groups/{group_id}/logs")
async def get_logs(group_id: str, user=Depends(require_role("site-admin"))):
    return service.get_logs(group_id)

@router.post("/groups/{group_id}/logs")
async def add_log(group_id: str, action: str, user=Depends(require_role("site-admin"))):
    return service.add_log(group_id, action)

# =======================
# FILES (Import/Export)
# =======================

@router.post("/groups/{group_id}/import")
async def import_file(group_id: str, file: UploadFile = File(...), user=Depends(require_role("site-admin"))):
    # You can parse CSV/Excel here and call service.replace_recipients
    content = await file.read()
    # TODO: parse content into emails list
    emails = []  # placeholder
    return service.replace_recipients(group_id, emails)

@router.get("/groups/{group_id}/export")
async def export_file(group_id: str, format: str = "csv", user=Depends(require_role("site-admin"))):
    # TODO: generate CSV/Excel from recipients
    recipients = service.get_group(group_id).get("recipients", [])
    return {"format": format, "recipients": recipients}


# =======================
# FILE IMPORT
# =======================

@router.post("/groups/{group_id}/import")
async def import_file(
    group_id: str,
    file: UploadFile = File(...),
    user=Depends(require_role("site-admin"))
):
    try:
        content = await file.read()
        emails: List[str] = []

        if file.filename.endswith(".csv"):
            decoded = content.decode("utf-8").splitlines()
            reader = csv.reader(decoded)
            for row in reader:
                if row:  # assume first column is email
                    emails.append(row[0].strip())
        elif file.filename.endswith((".xls", ".xlsx")):
            df = pd.read_excel(io.BytesIO(content))
            # assume there is a column named "email"
            emails = df["email"].dropna().astype(str).tolist()
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        service.replace_recipients(group_id, emails)
        return {"message": f"Imported {len(emails)} recipients", "emails": emails}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =======================
# FILE EXPORT
# =======================

@router.get("/groups/{group_id}/export")
async def export_file(
    group_id: str,
    format: str = "csv",
    user=Depends(require_role("site-admin"))
):
    group = service.get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    recipients = group.get("recipients", [])

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["email"])
        for email in recipients:
            writer.writerow([email])
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={group_id}.csv"}
        )

    elif format in ("xls", "xlsx"):
        df = pd.DataFrame({"email": recipients})
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={group_id}.xlsx"}
        )

    else:
        raise HTTPException(status_code=400, detail="Unsupported export format")
