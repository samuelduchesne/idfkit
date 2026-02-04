"""Tests for idfkit.weather.station."""

from __future__ import annotations

import pytest

from idfkit.weather.station import SearchResult, SpatialResult, WeatherStation


def _make_station(**kwargs: object) -> WeatherStation:
    defaults = {
        "country": "USA",
        "state": "IL",
        "city": "Chicago.Ohare.Intl.AP",
        "wmo": 725300,
        "source": "SRC-TMYx",
        "latitude": 41.98,
        "longitude": -87.92,
        "timezone": -6.0,
        "elevation": 201.0,
        "url": "https://climate.onebuilding.org/WMO_Region_4/USA_IL_Chicago.Ohare.Intl.AP.725300_TMYx.2009-2023.zip",
    }
    defaults.update(kwargs)
    return WeatherStation(**defaults)  # type: ignore[arg-type]


class TestWeatherStation:
    def test_display_name(self) -> None:
        s = _make_station()
        assert s.display_name == "Chicago Ohare Intl AP, IL, USA"

    def test_display_name_no_state(self) -> None:
        s = _make_station(state="")
        assert s.display_name == "Chicago Ohare Intl AP, USA"

    def test_dataset_variant_with_year_range(self) -> None:
        s = _make_station()
        assert s.dataset_variant == "TMYx.2009-2023"

    def test_dataset_variant_without_year_range(self) -> None:
        s = _make_station(
            url="https://climate.onebuilding.org/WMO_Region_4/USA_IL_Chicago.Ohare.Intl.AP.725300_TMYx.zip"
        )
        assert s.dataset_variant == "TMYx"

    def test_frozen(self) -> None:
        s = _make_station()
        with pytest.raises(AttributeError):
            s.wmo = 999999  # type: ignore[misc]


class TestSearchResult:
    def test_fields(self) -> None:
        s = _make_station()
        r = SearchResult(station=s, score=0.95, match_field="name")
        assert r.score == 0.95
        assert r.match_field == "name"


class TestSpatialResult:
    def test_fields(self) -> None:
        s = _make_station()
        r = SpatialResult(station=s, distance_km=12.5)
        assert r.distance_km == 12.5
