class DeviceService:
    def __init__(self, df):
        self.df = df

    def clockings_count(self):
        clockings_count = (
            self.df
            .groupby(["MeterID", "Date"])
            .size()
            .reset_index(name="Clocking_Count")
        )

        return clockings_count
