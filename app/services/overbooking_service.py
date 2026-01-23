import pandas as pd

class OverbookingService:
    def __init__(self, df):
        self.df = df.copy()
        self.overtime_codes = [101, 601, 602, 603, 604, 801, 802, 803, 804]
        self.daily_required = {
            0: 8.75,  # Monday
            1: 8.75,  # Tuesday
            2: 8.75,  # Wednesday
            3: 8.75,  # Thursday
            4: 5,     # Friday
            5: 0,     # Saturday
            6: 0      # Sunday
        }

    def find_duplicates_overtime(self):
        overtime_df = self.df[self.df["VIP Code"].isin(self.overtime_codes)]
        duplicates = overtime_df[overtime_df.duplicated(
            subset=["Resource no.", "Work date", "VIP Code", "Hours worked"],
            keep="first"
        )]
        return duplicates[
            ["Resource no.", "User Originator", "Work date", "VIP Code", "Hours worked"]
        ]

    def find_overbooked_normal_daily(self):
        norm_df = self.df[~self.df["VIP Code"].isin(self.overtime_codes)].copy()
        norm_df["Work date"] = pd.to_datetime(norm_df["Work date"])
        norm_df["week"] = norm_df["Work date"].dt.to_period("W-SAT")
        norm_df["weekday"] = norm_df["Work date"].dt.weekday
        norm_df["required_norm"] = norm_df["weekday"].map(self.daily_required)
        norm_df["cum_sum"] = norm_df.groupby(
            ["Resource no.", "Work date"]
        )["Hours worked"].cumsum()
        overbooked = norm_df[norm_df["cum_sum"] > norm_df["required_norm"]]
        return overbooked[
            [
                "Resource no.",
                "User Originator",
                "Work date",
                "VIP Code",
                "Hours worked",
                "cum_sum",
                "required_norm",
                "week",
                "weekday",
            ]
        ]

    def count_user_originators(self, df):
        """
        Count how many entries each User Originator has in the given DataFrame.
        Returns a DataFrame with counts sorted descending.
        """
        return (
            df["User Originator"]
            .value_counts()
            .reset_index()
            .rename(columns={"index": "User Originator", "User Originator": "count"})
        )

    @staticmethod
    def  count_user_originators(df) -> pd.DataFrame:
       
        counts = (
            df.groupby("User Originator")
            .size()
            .reset_index(name="incorrect_entry_count")
            .sort_values(by="incorrect_entry_count", ascending=False)
            .reset_index(drop=True)
        )
        return counts