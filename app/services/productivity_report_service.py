import pandas as pd

class ProductivityReportService:
    def __init__(self, df_hours_worked, df_hours_posted):
        self.df_hours_worked = df_hours_worked.copy()
        self.df_hours_posted = df_hours_posted.copy()

        # Define productive VIP codes
        self.productive_codes = [
            100, 110, 111, 113, 114, 115, 116, 117,
            290, 601, 602, 603, 604, 700, 750, 752,
            801, 802, 803, 804
        ]

    def hours_worked_by_clerk(self):
        self.df_hours_worked["Work date"] = pd.to_datetime(self.df_hours_worked["Work date"])
        df_clerk_hours = self.df_hours_worked[self.df_hours_worked["VIP Code"].isin(self.productive_codes)].copy()
        return df_clerk_hours.groupby(["Resource no.", "Work date"])["Hours worked"].sum().reset_index(name="Hours worked")

    def productive_hours_posted(self):
        self.df_hours_posted["Posting Date"] = pd.to_datetime(self.df_hours_posted["Posting Date"])
        posted_productive_df = self.df_hours_posted[self.df_hours_posted["VIP Code"].isin(self.productive_codes)].copy()
        return posted_productive_df.groupby(["User Originator", "Posting Date"])["Entry No."].count().reset_index(name="Entries posted")

    def allowance_posted(self):
        self.df_hours_posted["Posting Date"] = pd.to_datetime(self.df_hours_posted["Posting Date"])
        mask = self.df_hours_posted["VIP Code"].isin([101]) | (self.df_hours_posted["VIP Code"] >= 900)
        df_posted_allowance = self.df_hours_posted[mask].copy()
        return df_posted_allowance.groupby(["User Originator", "Posting Date"])["Entry No."].count().reset_index(name="Entries posted")

    def get_summary(self):
        df_hours_worked = self.hours_worked_by_clerk()
        df_allowance_entries_posted = self.allowance_posted()
        df_productive_entries_posted = self.productive_hours_posted()

        # ⚠️ Adjust this depending on whether you want to group by Resource no. or User Originator
        hours_worked_total = df_hours_worked.groupby(["Resource no."])["Hours worked"].sum().reset_index(name="Hours worked")

        total_posted_concat = pd.concat([df_allowance_entries_posted, df_productive_entries_posted], ignore_index=True)
        total_posted = total_posted_concat.groupby(["User Originator"])["Entries posted"].sum().reset_index(name="Entries posted")

        # Merge carefully: Resource no. vs User Originator mismatch
        summary_df = pd.merge(hours_worked_total, total_posted, left_on="Resource no.", right_on="User Originator", how="left")

        return summary_df
