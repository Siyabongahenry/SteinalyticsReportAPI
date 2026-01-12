import pandas as pd
class ProductivityReportService:
    def __init__(self,df_hours_worked,df_hours_posted):
        self.df_hours_worked = df_hours_worked
        self.df_hours_posted = df_hours_posted

    def hours_worked_by_clerk(self):

        self.df_hours_worked["Work date"] = pd.to_datetime(self.df_hours_worked["Work date"])

        df_clerk_hours = self.df_hours_worked[self.df_hours_worked["VIP Code"].isin([100,110,111,113,114,115,116,117,290,601,602,603,604,700,750,752,801,802,803,804])].copy()
        
        return df_clerk_hours.groupby(["Resource no.", "Work date"])["Hours worked"].sum().reset_index()
    
    def productive_hours_posted(self):

        self.df_hours_posted["Posting Date"] = pd.to_datetime(self.df_hours_posted["Posting Date"])

        posted_productive_df = self.df_hours_posted[self.df_hours_posted["VIP Code"].isin([100,110,111,113,114,115,116,117,290,601,602,603,604,700,750,752,801,802,803,804])].copy()

        return posted_productive_df.groupby([ "User Originator", "Posting Date"])["Entry No."].count().reset_index()

    def allowance_posted(self):

         self.df_hours_posted["Posting Date"] = pd.to_datetime(self.df_hours_posted["Posting Date"])

         df_posted_allowance = self.df_hours_posted[self.df_hours_posted["VIP Code"].isin[101] or self.df_hours_posted["VIP Code"] >= 900 ]
        
         return df_posted_allowance.groupby(["Entry No.","Posting Date"]).count().reset_index()



