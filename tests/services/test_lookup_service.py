import pandas as pd
import pytest
from app.services.lookup_service import LookupService   # adjust import path


@pytest.fixture
def df1():
    return pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"]
    })


@pytest.fixture
def df2():
    return pd.DataFrame({
        "id": [1, 2],
        "age": [25, 30]
    })


@pytest.fixture
def df3():
    return pd.DataFrame({
        "id": [2, 3],
        "city": ["NY", "LA"]
    })


def test_join_multiple_dataframes(df1, df2, df3):
    service = LookupService([df1, df2, df3], join_by_column="id")
    result = service.join_reports()

    # Expected: all rows from df1 preserved
    assert set(result["id"]) == {1, 2, 3}
    # Check merged columns exist
    assert "age" in result.columns
    assert "city" in result.columns
    # Verify specific joins
    row_bob = result[result["name"] == "Bob"].iloc[0]
    assert row_bob["age"] == 30
    assert row_bob["city"] == "NY"


def test_left_join_preserves_base_rows(df1, df2):
    service = LookupService([df1, df2], join_by_column="id")
    result = service.join_reports()

    # Charlie should still be present even though not in df2
    assert "Charlie" in result["name"].values
    # Age for Charlie should be NaN
    assert pd.isna(result[result["name"] == "Charlie"]["age"]).all()


def test_no_reports_raises():
    service = LookupService([], join_by_column="id")
    with pytest.raises(ValueError, match="No reports provided"):
        service.join_reports()
