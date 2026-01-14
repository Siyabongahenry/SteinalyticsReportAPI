import pandas as pd
from pandas.testing import assert_frame_equal
import pytest
from app.services.device_service import DeviceService   # adjust import to your module name

def test_clockings_count():
    # Arrange
    data = {
        "MeterID": [1, 1, 1, 2, 2],
        "Date": ["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-01", "2024-01-01"]
    }
    df = pd.DataFrame(data)
    service = DeviceService(df)

    # Act
    result = service.clockings_count()

    # Expected
    expected = pd.DataFrame({
        "MeterID": [1, 1, 2],
        "Date": ["2024-01-01", "2024-01-02", "2024-01-01"],
        "Clocking_Count": [2, 1, 2]
    })

    # Assert
    assert_frame_equal(
        result.sort_values(by=["MeterID", "Date"]).reset_index(drop=True),
        expected.sort_values(by=["MeterID", "Date"]).reset_index(drop=True)
    )
