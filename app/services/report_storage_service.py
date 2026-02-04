import uuid
from datetime import datetime,timezone
from app.core.dynamoDB import get_table  # your helper

class ReportStorageService:
    def __init__(self, table_name: str = "ExemptionReports"):
        self.table = get_table(table_name)

    def save_report(self, user_id: str, download_url: str, dfs: dict, report_type: str):
        """
        Save report metadata and dataframes to DynamoDB.
        dfs: dict of {sheet_name: pandas.DataFrame}
        """
        report_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        # Convert DataFrames to JSON-serializable format
        serialized_dfs = {
            sheet: df.to_dict(orient="records") for sheet, df in dfs.items()
        }

        item = {
            "ReportId": report_id,
            "UserId": user_id,
            "ReportType": report_type,
            "DownloadUrl": download_url,
            "DataFrames": serialized_dfs,
            "CreatedAt": timestamp,
        }

        self.table.put_item(Item=item)
        return report_id
