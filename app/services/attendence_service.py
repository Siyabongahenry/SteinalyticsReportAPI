import pandas as pd
class AttendanceService:
    def __init__(self, df: pd.DataFrame):
        # Make a copy to avoid modifying original
        self.df = df.copy()
        # Ensure Date column is datetime and only contains the date part (no time)
        self.df["Date"] = pd.to_datetime(self.df["Date"]).dt.date

    def get_employees_list(self) -> pd.DataFrame:
        """
        Returns a DataFrame of unique employee attendances.
        Each row represents one employee (Clock No.) attending a site (WTT) on a particular date.
        Multiple scans on the same day and site are ignored.
        """
        # Drop duplicates so each employee per site per day is counted only once
        attendance_list = self.df.drop_duplicates(subset=["WTT", "Date", "Clock No."])
        return attendance_list

    def get_summary_by_site(self) -> pd.DataFrame:
        """
        Returns a summary of attendance per site per day.
        Each row represents a site (WTT) on a specific date and the total
        number of unique employees who attended that site on that day.
        """
        # Remove duplicate scans for each employee per site per day
        unique_attendance = self.df.drop_duplicates(subset=["WTT", "Date", "Clock No."])
        # Group by site and date, count unique employees
        attendance_summary = (
            unique_attendance
            .groupby(["WTT", "Date"])
            .size()
            .reset_index(name="attendance")
        )
        return attendance_summary

    def get_attendance_by_employee_week(self) -> pd.DataFrame:
        """
        Returns attendance per employee per week.
        Attendance is counted as number of days present in a week.
        """
        df = self.df.copy()
        # Remove duplicate scans so each employee is counted once per day
        df = df.drop_duplicates(subset=["Clock No.", "Date"])
        # Create a weekly period column
        df["week"] = pd.to_datetime(df["Date"]).dt.to_period("W")
        # Group by employee and week, then count attendance days
        attendance = (
            df.groupby(["Clock No.", "week"])
              .size()
              .reset_index(name="attendance_days")
        )
        return attendance

    def get_attendance_by_employee_month(self) -> pd.DataFrame:
        """
        Returns attendance per employee per month.
        Attendance is counted as number of days present in a month.
        """
        df = self.df.copy()
        # Remove duplicate scans so each employee is counted once per day
        df = df.drop_duplicates(subset=["Clock No.", "Date"])
        # Create a monthly period column
        df["month"] = pd.to_datetime(df["Date"]).dt.to_period("M")
        # Group by employee and month, then count attendance days
        attendance = (
            df.groupby(["Clock No.", "month"])
              .size()
              .reset_index(name="attendance_days")
        )
        return attendance
