
import pandas as pd
import pytest

from who_app.metrics import WHOMetrics


def create_test_data():
    return pd.DataFrame({
        "COUNTRY_REGION": ["ESP", "ESP", "ESP", "FRA", "FRA"],
        "YEAR": [2020, 2021, 2022, 2020, 2021],
        "HFA_1_ALL": [100, 110, 105, 200, 220]})


def test_percentage_change():
    frame = create_test_data()
    metrics = WHOMetrics()
    result = metrics.percentage_change(
        frame,
        indicator="HFA_1_ALL",
        start_year=2020,
        end_year=2022
    )

    españa = result[result["COUNTRY_REGION"] == "ESP"]

    assert españa.iloc[0]["percentage_change"] == pytest.approx(5.0)
    assert len(result) == 1

def test_yearly_change():
    frame = create_test_data()
    metrics = WHOMetrics()

    result = metrics.yearly_change(
        frame,
        indicator="HFA_1_ALL",
        country="ESP"
    )

    assert pd.isna(result.iloc[0]["yearly_change"])
    assert result.iloc[1]["yearly_change"] == 10
    assert result.iloc[2]["yearly_change"] == -5
    assert len(result) == 3


def test_country_ranking():
    frame = create_test_data()
    metrics = WHOMetrics()

    result = metrics.country_ranking(
        frame,
        indicator="HFA_1_ALL",
        year=2020
    )

    assert result.iloc[0]["COUNTRY_REGION"] == "FRA"
    assert result.iloc[1]["COUNTRY_REGION"] == "ESP"
    assert result.iloc[0]["HFA_1_ALL"] == 200


def test_invalid_indicator():
    frame = create_test_data()
    metrics = WHOMetrics()

    with pytest.raises(ValueError):
        metrics.percentage_change(
            frame,
            indicator="HFA_9999_ALL",
            start_year=2020,
            end_year=2022
        )