import pandas as pd
import pytest
from app.utils.reversed_entries_utils import remove_reversed_entries  # adjust import path if needed


def test_remove_reversed_entries():
    # Sample DataFrame
    data = [
        {"Entry No.": 1, "Hours worked": 5, "Applies-To Entry": None},   # normal entry
        {"Entry No.": 2, "Hours worked": -5, "Applies-To Entry": 1},     # reversed entry (targets 1)
        {"Entry No.": 3, "Hours worked": 8, "Applies-To Entry": None},   # normal entry
        {"Entry No.": 4, "Hours worked": -8, "Applies-To Entry": 3},     # reversed entry (targets 3)
        {"Entry No.": 5, "Hours worked": 10, "Applies-To Entry": None},  # normal entry
    ]
    df = pd.DataFrame(data)

    # Apply function
    cleaned_df = remove_reversed_entries(df)

    # Expected: entries 1,2,3,4 removed; only entry 5 remains
    expected_df = pd.DataFrame([
        {"Entry No.": 5, "Hours worked": 10, "Applies-To Entry": None}
    ])

    # Reset index for comparison
    pd.testing.assert_frame_equal(
        cleaned_df.reset_index(drop=True),
        expected_df.reset_index(drop=True)
    )


def test_no_reversed_entries():
    # DataFrame with no reversed entries
    data = [
        {"Entry No.": 1, "Hours worked": 5, "Applies-To Entry": None},
        {"Entry No.": 2, "Hours worked": 7, "Applies-To Entry": None},
    ]
    df = pd.DataFrame(data)

    cleaned_df = remove_reversed_entries(df)

    # Should remain unchanged
    pd.testing.assert_frame_equal(
        cleaned_df.reset_index(drop=True),
        df.reset_index(drop=True)
    )


def test_reversed_entry_without_target():
    # Reversed entry points to a non-existent target
    data = [
        {"Entry No.": 1, "Hours worked": -5, "Applies-To Entry": 99},  # reversed entry
        {"Entry No.": 2, "Hours worked": 10, "Applies-To Entry": None},
    ]
    df = pd.DataFrame(data)

    cleaned_df = remove_reversed_entries(df)

    # Entry 1 should be removed, entry 2 remains
    expected_df = pd.DataFrame([
        {"Entry No.": 2, "Hours worked": 10, "Applies-To Entry": None}
    ])

    pd.testing.assert_frame_equal(
        cleaned_df.reset_index(drop=True),
        expected_df.reset_index(drop=True)
    )
