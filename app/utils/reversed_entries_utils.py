import pandas as pd

def remove_reversed_entries(df: pd.DataFrame) -> pd.DataFrame:
    """
    Removes reversed entries from the hours journal.
    A reversed entry is defined as a row with negative 'Hours worked' and a non-null 'Applies-To Entry'.
    The matching positive entry is identified by its 'Entry No.' matching the 'Applies-To Entry' value.
    Both entries are removed.

    Args:
        df (pd.DataFrame): Raw hours journal DataFrame.

    Returns:
        pd.DataFrame: Cleaned DataFrame with reversed entries and their targets removed.
    """
    # Identify reversed entries
    reversed_mask = (df["Hours worked"] < 0) & df["Applies-To Entry"].notnull()
    reversed_entries = df[reversed_mask]

    # Get Entry Nos to remove: both reversed and their targets
    reversed_entry_nos = set(reversed_entries["Entry No."])
    target_entry_nos = set(reversed_entries["Applies-To Entry"])

    all_entry_nos_to_remove = reversed_entry_nos.union(target_entry_nos)

    # Filter out all matching entries
    cleaned_df = df[~df["Entry No."].isin(all_entry_nos_to_remove)].copy()
    return cleaned_df