class DeviceService:
    def __init__(self, df):
        self.df = df

    def unique_clocks_per_meter_per_day(self):
        result = (
            self.df
            .groupby(["MeterID", "Date"])["Clock No."]
            .nunique()
            .reset_index(name="Unique_Clock_Count")
        )

        return result
