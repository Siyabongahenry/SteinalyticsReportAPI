import pandas as pd
from typing import List

class LookupService:
    def __init__(self, df_reports: List[pd.DataFrame], join_by_column: str):
        """
        df_reports: list of DataFrames
        join_by_column: column name to join on
        """
        self.df_reports = df_reports
        self.join_by_column = join_by_column

    def join_reports(self) -> pd.DataFrame:
        if not self.df_reports:
            raise ValueError("df_reports list is empty")

        # First DataFrame is the main one
        final_df = self.df_reports[0]

        # Left join remaining DataFrames
        for df in self.df_reports[1:]:
            final_df = final_df.merge(
                df,
                on=self.join_by_column,
                how="left"
            )

        return final_df
