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

    def find_duplicates_overtime(self):
        # Only check duplicates among overtime entries
        overtime_df = self.df[self.df["VIP Code"].isin(self.overtime_codes)]
        return overtime_df[overtime_df.duplicated(
            subset=["Resource no.", "Work date", "VIP Code", "Hours worked"],
            keep="first"
        )]

    def find_overbooked_normal_daily(self):
        # Filter normal (non-overtime) entries
        norm_df = self.df[~self.df["VIP Code"].isin(self.overtime_codes)].copy()
        norm_df["Work date"] = pd.to_datetime(norm_df["Work date"])

        # Add week and weekday info
        norm_df["week"] = norm_df["Work date"].dt.to_period("W-SAT")
        norm_df["weekday"] = norm_df["Work date"].dt.weekday
        norm_df["required_norm"] = norm_df["weekday"].map(self.daily_required)

        # Compute cumulative hours per resource per day
        norm_df["cum_sum"] = norm_df.groupby(
            ["Resource no.", "Work date"]
        )["Hours worked"].cumsum()

        # Return rows where cumulative exceeds required
        return norm_df[norm_df["cum_sum"] > norm_df["required_norm"]]
