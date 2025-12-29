import pandas as pd

class OverbookingService:
    def __init__(self,df):
        self.df = df.copy()
        self.overtime_codes = [101,601,602,603,604,801,802,803,804]
        self.daily_required = {
            0:8.75,
            1:8.75,
            2:8.75,
            3:8.75,
            4:5,
            5:0,
            6:0
        }
        

    def find_duplicates_overtime(self):
        
        overtime_filter = self.df[self.df["VIP Code"].isin(self.overtime_codes)]

        return self.df[self.df.duplicated(subset=["Resource no.","Work date","VIP Code","Hours worked"],keep="first")]
    
    def find_overbooked_normal_daily(self):

        normal_entries = self.df[~self.df["VIP Code"].isin(self.overtime_codes)]

        norm_df = self.df[normal_entries]

        norm_df["Work date"] = pd.to_datetime(norm_df["Work date"])

        norm_df["week"] = norm_df["Work date"].dt.to_period("W-SAT")

        norm_df["weekday"] = norm_df["Work date"].dt.weekday

        norm_df["required_norm"] = norm_df["weekday"].map(self.daily_required)

        norm_df["cum_sum"] = norm_df.groupby(["Resource no.","Work date"])["Hours worked"].cumsum()
        
        normal_required_filter = norm_df["cum_sum"]

        return norm_df[norm_df["cum_sum"] > norm_df["required_norm"]]