import json
import pandas as pd

from app.utils.date_utils import get_weekday_number, is_public_holiday

class IncorrectVIPService:
    def __init__(self, df: pd.DataFrame, config_path: str):
        self.df = df.copy()
        self.df["Work date"] = pd.to_datetime(self.df["Work date"]).dt.date
        self.rules = self._load_rules(config_path)

    def _load_rules(self, path: str) -> dict:
        with open(path, "r") as f:
            return json.load(f)["hour_codes"]

    def find_incorrect_vip(self) -> pd.DataFrame:
        df = self.df
        df["VIP Code"] = df["VIP Code"].astype(int)
        df["_weekday"] = df["Work date"].map(get_weekday_number)
        df["_is_holiday"] = df["Work date"].map(is_public_holiday)

        weekday_map = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 
                       4: "Friday", 5: "Saturday", 6: "Sunday"}
        df["Day Name"] = df["_weekday"].map(weekday_map)
        df.loc[df["_is_holiday"], "Day Name"] = "Holiday"

        mon_fri_codes = set(self.rules["mon_fri_normal"] + self.rules["mon_fri_overtime"] + self.rules["driver"])
        saturday_codes = set(self.rules["saturday_overtime"] + self.rules["driver"])
        sunday_codes = set(self.rules["sunday_overtime"] + self.rules["driver"])
        holiday_codes = set(self.rules["holiday_normal"] + self.rules["holiday_overtime"] + self.rules["driver"])

        is_sunday = df["_weekday"] == 6
        is_saturday = df["_weekday"] == 5
        is_holiday = df["_is_holiday"]
        is_mon_fri = df["_weekday"].between(0, 4)

        incorrect_mask = (
            (is_sunday & ~df["VIP Code"].isin(sunday_codes)) |
            (is_holiday & ~is_sunday & ~df["VIP Code"].isin(holiday_codes)) |
            (is_saturday & ~is_holiday & ~df["VIP Code"].isin(saturday_codes)) |
            (is_mon_fri & ~is_holiday & ~df["VIP Code"].isin(mon_fri_codes))
        )

        important_cols = ["Entry No.", "Resource no.", "Work date", "Day Name", "VIP Code", 
                          "Hours worked", "User Originator"]

        result = df.loc[incorrect_mask, important_cols]
        return result.reset_index(drop=True)

    @staticmethod
    def count_incorrect_entries_per_originator(incorrect_df: pd.DataFrame) -> pd.DataFrame:
        """
        Count how many incorrect VIP entries each User Originator has.
        Accepts the filtered incorrect DataFrame as input.
        """
        counts = (
            incorrect_df.groupby("User Originator")
            .size()
            .reset_index(name="incorrect_entry_count")
            .sort_values(by="incorrect_entry_count", ascending=False)
            .reset_index(drop=True)
        )
        return counts
