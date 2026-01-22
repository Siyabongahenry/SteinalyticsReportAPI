import pandas as pd


class OverbookingService:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

        # Overtime VIP codes
        self.overtime_codes = [101, 601, 602, 603, 604, 801, 802, 803, 804]

        # Required normal working hours per weekday
        self.daily_required = {
            0: 8.75,  # Monday
            1: 8.75,  # Tuesday
            2: 8.75,  # Wednesday
            3: 8.75,  # Thursday
            4: 5.00,  # Friday
            5: 0.00,  # Saturday
            6: 0.00,  # Sunday
        }

    def find_duplicates_overtime(self) -> pd.DataFrame:
        """
        Find duplicated overtime entries for the same resource and day.
        """

        overtime_df = self.df[self.df["VIP Code"].isin(self.overtime_codes)]

        duplicates = overtime_df[overtime_df.duplicated(
            subset=[
                "Resource no.",
                "Work date",
                "VIP Code",
                "Hours worked",
            ],
            keep="first",
        )]

        return duplicates[
            [
                "Resource no.",
                "Work date",
                "VIP Code",
                "Hours worked",
                "User Originator"
            ]
        ]

    def find_overbooked_normal_daily(self) -> pd.DataFrame:
        """
        Find normal (non-overtime) workdays where daily hours exceed
        the required working hours.
        """

        # Filter non-overtime entries
        norm_df = self.df[~self.df["VIP Code"].isin(self.overtime_codes)].copy()

        # Ensure datetime
        norm_df["Work date"] = pd.to_datetime(norm_df["Work date"])

        # Weekday and required hours
        norm_df["weekday"] = norm_df["Work date"].dt.weekday
        norm_df["required_norm"] = norm_df["weekday"].map(self.daily_required)

        # Cumulative daily hours per resource
        norm_df["cum_sum"] = norm_df.groupby(
            ["Resource no.", "Work date"]
        )["Hours worked"].cumsum()

        # Overbooked rows
        overbooked = norm_df[norm_df["cum_sum"] > norm_df["required_norm"]]

        return overbooked[
            [
                "Resource no.",
                "Work date",
                "VIP Code"
                "Hours worked",
                "cum_sum",
                "required_norm",
                "User Originator"
            ]
        ]
