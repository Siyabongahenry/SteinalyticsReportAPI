class MultipleClockingsService:

    def __init__(self, df):
        self.df = df

    def getMultipleClockings(self):
        occurrence_count = (
            self.df
            .groupby(["Clock No.","Date"])
            .transform("size")
        )

        return self.df[occurrence_count > 3]
