import pandas as pd

class ExemptionService:
    def __init__(self, df: pd.DataFrame, type: str):
        self.df = df
        self.type = type
    
    def get_week_exemption(self):
        self.df["Work date"] = pd.to_datetime(self.df["Work date"])
        
        # Compute week start (Sunday) and week end (Saturday)
        week_start = self.df["Work date"] - pd.to_timedelta((self.df["Work date"].dt.weekday + 1) % 7, unit="D")
        week_end = week_start + pd.Timedelta(days=6)
        
        # Add formatted week string
        self.df["Week"] = week_start.dt.strftime("%Y.%m.%d") + "/" + week_end.dt.strftime("%Y.%m.%d")
        
        # Group by Resource no. and Week, summing hours
        grouped = (
            self.df.groupby(["Resource no.", "Week"], as_index=False)["Hours worked"]
            .sum()
        )
        
        # Filter employees with >72 hours
        grouped = grouped[grouped["Hours worked"] > 72].copy()
        
        # Add exemption and excess columns
        grouped["Exemption: 72"] = 72
        grouped["Excess"] = grouped["Hours worked"] - 72
        
        return grouped[["Resource no.", "Week", "Exemption: 72", "Excess"]]
    
    def get_month_exemption(self):
        # First compute weekly excess
        weekly_excess = self.get_week_exemption()
        
        # Extract month from week start (first date in week string)
        weekly_excess["Month"] = pd.to_datetime(
            weekly_excess["Week"].str.split("/").str[0], format="%Y.%m.%d"
        ).dt.strftime("%Y.%m")
        
        # Group by Resource no. and Month, summing excess
        monthly = (
            weekly_excess.groupby(["Resource no.", "Month"], as_index=False)["Excess"]
            .sum()
        )
        
        # Add exemption column (still 72 per week, but monthly we show total excess)
        monthly["Exemption: 72"] = 72
        
        return monthly[["Resource no.", "Month", "Exemption: 72", "Excess"]]
    
    def get_exemption(self):
        if self.type == "week":
            return self.get_week_exemption()
        elif self.type == "month":
            return self.get_month_exemption()
        else:
            raise ValueError("Type must be 'week' or 'month'")
