import pandas as pd
from typing import List

class LookupService:
    """
    Service responsible for joining multiple DataFrames.
    The first DataFrame is treated as the main table.
    All other DataFrames are LEFT JOINED to it.
    """

    def __init__(self, df_reports: List[pd.DataFrame], join_by_column: str):
        # List of DataFrames to join
        self.df_reports = df_reports

        # Column name used for joining
        self.join_by_column = join_by_column

    def join_reports(self) -> pd.DataFrame:
        """
        Performs a LEFT JOIN on multiple DataFrames.

        Returns:
            pd.DataFrame: Final joined DataFrame
        """

        # Ensure at least one DataFrame exists
        if not self.df_reports:
            raise ValueError("No reports provided")

        # The first DataFrame is the base (main table)
        final_df = self.df_reports[0]

        # Iterate over remaining DataFrames and left join them
        for df in self.df_reports[1:]:
            final_df = final_df.merge(
                df,
                on=self.join_by_column,
                how="left"
            )

        return final_df
