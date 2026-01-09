import pandas as pd
class AttendanceService:
    def __init__(self,df):
        self.df = df

    def get_employees_list(self):
        """
        Returns a DataFrame of unique employee attendances.

        Each row represents one employee (Clock No.) attending a site (WTT) on a particular date.
        Multiple scans on the same day and site are ignored.
        """

        # Drop duplicates so each employee per site per day is counted only once
        attendance_list = self.df.drop_duplicates(
            subset=["WTT", "Date", "Clock No."]
        )

        return attendance_list

    
    def get_summary_by_site(self):
        """
        Returns a summary of attendance per site per day.

        Each row represents a site (WTT) on a specific date and the total
        number of unique employees who attended that site on that day.
        Multiple scans per employee are ignored.
        """

        # Remove duplicate scans for each employee per site per day
        unique_attendance = self.df.drop_duplicates(
            subset=["WTT", "Date", "Clock No."]
        )

        # Group by site and date, count unique employees
        attendance_summary = (
            unique_attendance
            .groupby(["WTT", "Date"])
            .size()
            .reset_index(name="attendance")
        )

        return attendance_summary

    
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

    def get_attendance_by_employee_month(self):
        """
        Returns attendance per employee per month.

        Business rules:
        - 'Clock No.' uniquely identifies an employee
        - An employee can only attend once per day
        - Multiple fingerprint scans in a day are ignored
        - Attendance is counted as number of days present in a month
        """

        # Work on a copy to avoid modifying the original DataFrame
        df = self.df.copy()

        # Ensure Date column is in datetime format
        df["Date"] = pd.to_datetime(df["Date"])

        # Remove duplicate scans so each employee is counted once per day
        df = df.drop_duplicates(subset=["Clock No.", "Date"])

        # Create a monthly period column from the Date
        df["month"] = df["Date"].dt.to_period("M")

        # Group by employee and month, then count attendance days
        attendance = (
            df
            .groupby(["Clock No.", "month"])
            .size()
            .reset_index(name="attendance_days")
        )

        return attendance
