import pandas as pd

class ExemptionService:
    def __init__(self, df: pd.DataFrame, type: str = "week"):
        self.df = df.copy()
        self.type = type
        # Ensure "Work date" is date only
        self.df["Work date"] = pd.to_datetime(self.df["Work date"]).dt.date

    def get_week_exemption(self) -> pd.DataFrame:
        """
        Returns weekly exemptions for employees.
        Week: Sunday to Saturday.
        Employees exceeding 72 hours/week are flagged.
        """
        df = self.df.copy()

        # Compute week start (Sunday) and week end (Saturday)
        week_start = pd.to_datetime(df["Work date"]) - pd.to_timedelta(
            (pd.to_datetime(df["Work date"]).dt.weekday + 1) % 7, unit="D"
        )
        week_end = week_start + pd.Timedelta(days=6)

        # Add formatted week string
        df["Week"] = week_start.dt.strftime("%Y.%m.%d") + "/" + week_end.dt.strftime("%Y.%m.%d")

        # Group by Resource no. and Week, summing hours
        grouped = df.groupby(["Resource no.", "Week"], as_index=False)["Hours worked"].sum()

        # Filter employees with >72 hours
        grouped = grouped[grouped["Hours worked"] > 72].copy()

        # Add exemption and excess columns
        grouped["Exemption"] = 72
        grouped["Excess"] = grouped["Hours worked"] - 72

        return grouped[["Resource no.", "Week", "Exemption", "Excess"]]

    def get_month_exemption(self) -> pd.DataFrame:
        """
        Returns monthly exemptions by summing weekly excesses.
        """
        weekly_excess = self.get_week_exemption()

        # Extract month from week start (first date in week string)
        weekly_excess["Month"] = pd.to_datetime(
            weekly_excess["Week"].str.split("/").str[0], format="%Y.%m.%d"
        ).dt.strftime("%Y.%m")

        # Group by Resource no. and Month, summing excess
        monthly = weekly_excess.groupby(["Resource no.", "Month"], as_index=False)["Excess"].sum()

        # Add exemption column (still 72 per week)
        monthly["Exemption"] = 72

        return monthly[["Resource no.", "Month", "Exemption", "Excess"]]

    def get_exemption(self) -> pd.DataFrame:
        if self.type == "week":
            return self.get_week_exemption()
        elif self.type == "month":
            return self.get_month_exemption()
        else:
            raise ValueError("Type must be 'week' or 'month'")
