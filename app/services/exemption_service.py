import pandas as pd

class ExemptionService:
    def __init__(self, df: pd.DataFrame, type: str = "week",productive_codes = None, unproductive_codes = None):
        self.df = df.copy()
        self.type = type
        self.unproductive_codes =unproductive_codes or [101,200,240,250,301,320,350,400,500]
        self.productive_codes = productive_codes or [100,290,601,602,603,604,700,750,751,801,802,803,804]
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
        
    def get_pivoted_exemption(self):
        df = self.df.copy()

        # Split into productive and unproductive
        productive_df = df[df["VIP Code"].isin(self.productive_codes)]
        unproductive_df = df[df["VIP Code"].isin(self.unproductive_codes)]

        # Pivot productive
        pivot_productive = pd.pivot_table(
            productive_df,
            values="Hours worked",
            index="Resource no.",
            columns="Work date",
            aggfunc="sum",
            fill_value=0
        )

        # Pivot unproductive
        pivot_unproductive = pd.pivot_table(
            unproductive_df,
            values="Hours worked",
            index="Resource no.",
            columns="Work date",
            aggfunc="sum",
            fill_value=0
        )

        # Ensure columns are datetime
        pivot_productive.columns = pd.to_datetime(pivot_productive.columns)
        pivot_unproductive.columns = pd.to_datetime(pivot_unproductive.columns)

        # Group columns into weeks and sum
        weekly_productive = pivot_productive.groupby(pd.Grouper(axis=1, freq="W")).sum()
        weekly_unproductive = pivot_unproductive.groupby(pd.Grouper(axis=1, freq="W")).sum()

        # Add weekly totals
        weekly_productive["Productive_Total"] = weekly_productive.sum(axis=1)
        weekly_unproductive["Unproductive_Total"] = weekly_unproductive.sum(axis=1)

        # Join side by side
        final_weekly = weekly_productive.join(
            weekly_unproductive,
            how="left",
            lsuffix="_prod",
            rsuffix="_unprod"
        )

        # Add final weekly total
        final_weekly["Final_Total"] = (
            final_weekly["Productive_Total"].fillna(0)
            + final_weekly["Unproductive_Total"].fillna(0)
        )

        # Calculate excess hours per week (never negative)
        final_weekly["Excess"] = (final_weekly["Final_Total"] - 72).clip(lower=0)

        # Add per-employee grand total of excess across all weeks
        final_weekly["Total_Excess"] = final_weekly.groupby("Resource no.")["Excess"].transform("sum")

        # Keep only employees who exceeded at least once
        exceeded_employees = final_weekly.groupby("Resource no.")["Excess"].sum() > 0
        final_weekly = final_weekly.loc[exceeded_employees]

        return final_weekly


