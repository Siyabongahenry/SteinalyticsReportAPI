from typing import List, Dict, Any, Optional
from app.core.dynamoDB import get_table
from app.core.settings import settings

class EmailOrganizerService:
    def __init__(self, db_table=None):
        self.table = db_table or get_table(settings.email_organizer_table)

    # =======================
    # GROUPS
    # =======================
    def create_group(self, group_id: str, name: str, managers: List[str] = None):
        item = {
            "groupId": group_id,
            "groupName": name,
            "managers": managers or [],
            "recipients": [],
            "logs": []
        }
        self.table.put_item(Item=item)
        return item

    def update_group(self, group_id: str, updates: Dict[str, Any]):
        self.table.update_item(
            Key={"groupId": group_id},
            UpdateExpression="SET " + ", ".join(f"{k}= :{k}" for k in updates),
            ExpressionAttributeValues={f":{k}": v for k, v in updates.items()},
            ReturnValues="ALL_NEW"
        )
        return {"message": f"Group {group_id} updated"}

    def get_group(self, group_id: str) -> Optional[Dict[str, Any]]:
        res = self.table.get_item(Key={"groupId": group_id})
        return res.get("Item")

    def delete_group(self, group_id: str):
        self.table.delete_item(Key={"groupId": group_id})
        return {"message": f"Group {group_id} deleted"}

    # =======================
    # RECIPIENTS
    # =======================
    def add_recipients(self, group_id: str, emails: List[str]):
        group = self.get_group(group_id)
        if not group:
            return None
        recipients = list(set(group.get("recipients", []) + emails))
        self.update_group(group_id, {"recipients": recipients})
        return recipients

    def replace_recipients(self, group_id: str, emails: List[str]):
        self.update_group(group_id, {"recipients": emails})
        return emails

    def remove_recipient(self, group_id: str, email: str):
        group = self.get_group(group_id)
        if not group:
            return None
        recipients = [r for r in group.get("recipients", []) if r != email]
        self.update_group(group_id, {"recipients": recipients})
        return recipients

    # =======================
    # MANAGERS
    # =======================
    def add_manager(self, group_id: str, user_id: str):
        group = self.get_group(group_id)
        managers = list(set(group.get("managers", []) + [user_id]))
        self.update_group(group_id, {"managers": managers})
        return managers

    def remove_manager(self, group_id: str, user_id: str):
        group = self.get_group(group_id)
        managers = [m for m in group.get("managers", []) if m != user_id]
        self.update_group(group_id, {"managers": managers})
        return managers

    # =======================
    # LOGS
    # =======================
    def add_log(self, group_id: str, action: str):
        group = self.get_group(group_id)
        logs = group.get("logs", [])
        logs.append({"action": action})
        self.update_group(group_id, {"logs": logs})
        return logs

    def get_logs(self, group_id: str):
        group = self.get_group(group_id)
        return group.get("logs", [])
