import json
import pandas as pd

from app.utils.date_utils import get_weekday_number, is_public_holiday

class IncorrectVIPService:
    def __init__(self, df: pd.DataFrame, config_path: str):
        # Make a copy of the dataframe
        self.df = df.copy()
        # Ensure Work date is only date (no time)
        self.df["Work date"] = pd.to_datetime(self.df["Work date"]).dt.date
        # Load rules from JSON config
        self.rules = self._load_rules(config_path)

    def _load_rules(self, path: str) -> dict:
        with open(path, "r") as f:
            return json.load(f)["hour_codes"]

    def find_incorrect_vip(self) -> pd.DataFrame:
        df = self.df

        # Normalize VIP Code column
        df["VIP Code"] = df["VIP Code"].astype(int)

        # Vectorized weekday & holiday flags
        df["_weekday"] = df["Work date"].map(get_weekday_number)
        df["_is_holiday"] = df["Work date"].map(is_public_holiday)

        # Map weekday number to name
        weekday_map = {
            0: "Monday",
            1: "Tuesday",
            2: "Wednesday",
            3: "Thursday",
            4: "Friday",
            5: "Saturday",
            6: "Sunday",
        }
        df["Day Name"] = df["_weekday"].map(weekday_map)

        # Override with "Holiday" if flagged
        df.loc[df["_is_holiday"], "Day Name"] = "Holiday"

        # Pre-build allowed code sets
        mon_fri_codes = set(
            self.rules["mon_fri_normal"]
            + self.rules["mon_fri_overtime"]
            + self.rules["driver"]
        )
        saturday_codes = set(self.rules["saturday_overtime"] + self.rules["driver"])
        sunday_codes = set(self.rules["sunday_overtime"] + self.rules["driver"])
        holiday_codes = set(
            self.rules["holiday_normal"] + self.rules["holiday_overtime"] + self.rules["driver"]
        )

        # Build rule masks
        is_sunday = df["_weekday"] == 6
        is_saturday = df["_weekday"] == 5
        is_holiday = df["_is_holiday"]
        is_mon_fri = df["_weekday"].between(0, 4)

        # Incorrect VIP masks per rule
        incorrect_sunday = is_sunday & ~df["VIP Code"].isin(sunday_codes)
        incorrect_holiday = is_holiday & ~is_sunday & ~df["VIP Code"].isin(holiday_codes)
        incorrect_saturday = is_saturday & ~is_holiday & ~df["VIP Code"].isin(saturday_codes)
        incorrect_mon_fri = is_mon_fri & ~is_holiday & ~df["VIP Code"].isin(mon_fri_codes)

        # Combine all incorrect rows
        incorrect_mask = incorrect_sunday | incorrect_holiday | incorrect_saturday | incorrect_mon_fri

        # Select important columns
        important_cols = [
            "Entry No.",
            "Resource no.",
            "Work date",
            "Day Name",
            "VIP Code",
            "Hours worked",
            "User Originator"
        ]

        # Return filtered dataframe with reset index
        result = df.loc[incorrect_mask, important_cols]
        return result.reset_index(drop=True)
