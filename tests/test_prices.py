import pandas as pd
import pytest

from haze_salience.data.prices import load_prices, save_prices


def test_round_trip_through_cache(tmp_path):
    df = pd.DataFrame(
        {"F34.SI": [3.0, 3.1], "^STI": [3500.0, 3510.0]},
        index=pd.to_datetime(["2026-10-15", "2026-10-16"]),
    )
    save_prices(df, tmp_path)
    out = load_prices(tmp_path)
    pd.testing.assert_frame_equal(out, df, check_freq=False, check_names=False)


def test_missing_cache_points_to_make_data(tmp_path):
    with pytest.raises(FileNotFoundError, match="make data"):
        load_prices(tmp_path)
