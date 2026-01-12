import pandas as pd
class ProductivityReportService:
    def __init__(self,df_hours_worked,df_hours_posted):
        self.df_hours_worked = df_hours_worked
        self.df_hours_posted = df_hours_posted

    def hours_worked_by_clerk(self):

        self.df_hours_worked["Work date"] = pd.to_datetime(self.df_hours_worked["Work date"])
        
        group = self.df_hours_worked.groupby(["Resource no.", "Work date"])["Hours worked"].sum().reset_index()

        return group
    
    def productive_hours_posted(self):

        self.df_hours_posted["Posting Date"] = pd.to_datetime(self.df_hours_posted["Posting Date"])

        group = self.df_hours_posted.groupby([ "User Originator", "Posting Date"])["Entry No."].count().reset_index()

        return group






