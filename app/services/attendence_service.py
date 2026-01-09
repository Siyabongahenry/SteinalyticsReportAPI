class AttendanceService:
    def __init__(self,df):
        self.df = df

    def get_employees_list(self):

        attendence_list = self.df.drop_duplicates(
            subset=["WTT", "Date", "Clock No."]
        )

        return attendence_list
    
    def get_summary_by_site(self):
        unique_attendance = self.df.drop_duplicates(
            subset=["WTT", "Date", "Clock No."]
        )

        return (
            unique_attendance
            .groupby(["WTT", "Date"])
            .size()
            .reset_index(name="attendance")
        )
