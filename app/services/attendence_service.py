import pandas as pd
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
    
    def get_attendance_by_employee_week(self):
        """
        Returns attendance per employee per week.

        Business rules:
        - 'Clock No.' uniquely identifies an employee
        - An employee can only attend once per day
        - Multiple fingerprint scans in a day are ignored
        - Attendance is counted as number of days present in a week
        """

        # Work on a copy to avoid modifying the original DataFrame
        df = self.df.copy()

        # Ensure Date column is in datetime format
        df["Date"] = pd.to_datetime(df["Date"])

        # Remove duplicate scans so each employee is counted once per day
        df = df.drop_duplicates(subset=["Clock No.", "Date"])

        # Create a weekly period column from the Date
        df["week"] = df["Date"].dt.to_period("W")

        # Group by employee and week, then count attendance days
        attendance = (
            df
            .groupby(["Clock No.", "week"])
            .size()
            .reset_index(name="attendance_days")
        )

        return attendance

