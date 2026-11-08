import pandas as pd
import pytest

from haze_salience.data.cpo import load_cpo, load_fcpo_csv

INVESTING_CSV = """"Date","Price","Open","High","Low","Vol.","Change %"
"10/16/2026","4,120.00","4,100.00","4,150.00","4,090.00","25.10K","0.49%"
"10/15/2026","4,100.00","4,080.00","4,110.00","4,070.00","22.00K","-0.24%"
"""

BARCHART_CSV = """Time,Open,High,Low,Last,Change,Volume
2026-10-15,4080,4110,4070,4100,-10,22000
2026-10-16,4100,4150,4090,4120,20,25100
"""


@pytest.mark.parametrize("text", [INVESTING_CSV, BARCHART_CSV])
def test_parses_common_vendor_formats(tmp_path, text):
    p = tmp_path / "fcpo.csv"
    p.write_text(text)
    s = load_fcpo_csv(p)
    assert list(s.index) == list(pd.to_datetime(["2026-10-15", "2026-10-16"]))
    assert list(s) == [4100.0, 4120.0]


def test_unrecognised_columns_raise(tmp_path):
    p = tmp_path / "fcpo.csv"
    p.write_text("foo,bar\n1,2\n")
    with pytest.raises(ValueError, match="date"):
        load_fcpo_csv(p)


def test_prefers_manual_csv(tmp_path):
    p = tmp_path / "fcpo.csv"
    p.write_text(BARCHART_CSV)

    def fallback():
        raise AssertionError("fallback should not be called")

    series, label = load_cpo(p, fallback)
    assert "FCPO" in label
    assert series.iloc[-1] == 4120.0


def test_falls_back_when_csv_missing(tmp_path):
    fb = pd.Series([1.0, 2.0], index=pd.to_datetime(["2026-10-15", "2026-10-16"]))
    series, label = load_cpo(tmp_path / "missing.csv", lambda: fb)
    assert "soybean" in label.lower()
    pd.testing.assert_series_equal(series, fb, check_names=False)
