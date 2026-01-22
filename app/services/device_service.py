import pandas as pd
class DeviceService:
    def __init__(self, df):
        self.df = df.copy()

        # Ensure Date is a datetime object
        self.df["Date"] = pd.to_datetime(self.df["Date"]).dt.date  # Keep only the date part

    def unique_clocks_per_meter_per_day(self):
        result = (
            self.df
            .groupby(["MeterID", "Date"])["Clock No."]
            .nunique()
            .reset_index(name="Unique_Clock_Count")
        )
        return result
