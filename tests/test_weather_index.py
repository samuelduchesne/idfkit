"""Tests for idfkit.weather.index (offline, no network)."""

from __future__ import annotations

from idfkit.weather.index import StationIndex
from idfkit.weather.station import WeatherStation


def _fixture_stations() -> list[WeatherStation]:
    """A small hand-crafted station list for search and spatial tests."""
    return [
        WeatherStation(
            country="USA",
            state="IL",
            city="Chicago.Ohare.Intl.AP",
            wmo=725300,
            source="SRC-TMYx",
            latitude=41.98,
            longitude=-87.92,
            timezone=-6.0,
            elevation=201.0,
            url="https://climate.onebuilding.org/WMO_Region_4_North_and_Central_America/USA_United_States_of_America/IL_Illinois/USA_IL_Chicago.Ohare.Intl.AP.725300_TMYx.2009-2023.zip",
        ),
        WeatherStation(
            country="USA",
            state="IL",
            city="Chicago.Midway.AP",
            wmo=725340,
            source="SRC-TMYx",
            latitude=41.79,
            longitude=-87.75,
            timezone=-6.0,
            elevation=189.0,
            url="https://climate.onebuilding.org/WMO_Region_4_North_and_Central_America/USA_United_States_of_America/IL_Illinois/USA_IL_Chicago.Midway.AP.725340_TMYx.2009-2023.zip",
        ),
        WeatherStation(
            country="USA",
            state="NY",
            city="New.York.J.F.Kennedy.Intl.AP",
            wmo=744860,
            source="SRC-TMYx",
            latitude=40.64,
            longitude=-73.76,
            timezone=-5.0,
            elevation=4.0,
            url="https://climate.onebuilding.org/WMO_Region_4_North_and_Central_America/USA_United_States_of_America/NY_New_York/USA_NY_New.York.J.F.Kennedy.Intl.AP.744860_TMYx.zip",
        ),
        WeatherStation(
            country="GBR",
            state="",
            city="London.Heathrow.AP",
            wmo=37720,
            source="SRC-TMYx",
            latitude=51.48,
            longitude=-0.45,
            timezone=0.0,
            elevation=25.0,
            url="https://climate.onebuilding.org/WMO_Region_6_Europe/GBR_United_Kingdom/GBR_London.Heathrow.AP.037720_TMYx.zip",
        ),
        WeatherStation(
            country="FRA",
            state="",
            city="Paris.Orly.AP",
            wmo=71490,
            source="SRC-TMYx",
            latitude=48.73,
            longitude=2.40,
            timezone=1.0,
            elevation=89.0,
            url="https://climate.onebuilding.org/WMO_Region_6_Europe/FRA_France/FRA_Paris.Orly.AP.071490_TMYx.zip",
        ),
    ]


class TestStationIndex:
    def test_len(self) -> None:
        idx = StationIndex.from_stations(_fixture_stations())
        assert len(idx) == 5

    def test_get_by_wmo(self) -> None:
        idx = StationIndex.from_stations(_fixture_stations())
        results = idx.get_by_wmo(725300)
        assert len(results) == 1
        assert results[0].city == "Chicago.Ohare.Intl.AP"

    def test_get_by_wmo_missing(self) -> None:
        idx = StationIndex.from_stations(_fixture_stations())
        assert idx.get_by_wmo(999999) == []


class TestSearch:
    def test_exact_wmo(self) -> None:
        idx = StationIndex.from_stations(_fixture_stations())
        results = idx.search("725300")
        assert len(results) >= 1
        assert results[0].station.wmo == 725300
        assert results[0].score == 1.0
        assert results[0].match_field == "wmo"

    def test_name_substring(self) -> None:
        idx = StationIndex.from_stations(_fixture_stations())
        results = idx.search("ohare")
        assert len(results) >= 1
        assert results[0].station.city == "Chicago.Ohare.Intl.AP"
        assert results[0].score > 0.8

    def test_multi_token(self) -> None:
        idx = StationIndex.from_stations(_fixture_stations())
        results = idx.search("chicago midway")
        assert len(results) >= 1
        assert results[0].station.wmo == 725340

    def test_country_filter(self) -> None:
        idx = StationIndex.from_stations(_fixture_stations())
        results = idx.search("ap", country="GBR")
        assert all(r.station.country == "GBR" for r in results)

    def test_empty_query(self) -> None:
        idx = StationIndex.from_stations(_fixture_stations())
        assert idx.search("") == []

    def test_no_match(self) -> None:
        idx = StationIndex.from_stations(_fixture_stations())
        results = idx.search("zzzznonexistent")
        assert results == []


class TestNearest:
    def test_nearest_to_chicago(self) -> None:
        idx = StationIndex.from_stations(_fixture_stations())
        # Downtown Chicago: 41.88, -87.63
        results = idx.nearest(41.88, -87.63, limit=3)
        assert len(results) == 3
        # Midway is closer to downtown than O'Hare
        assert results[0].station.wmo == 725340  # Midway
        assert results[1].station.wmo == 725300  # O'Hare
        # Distance should be reasonable
        assert results[0].distance_km < 30.0

    def test_max_distance_filter(self) -> None:
        idx = StationIndex.from_stations(_fixture_stations())
        results = idx.nearest(41.88, -87.63, max_distance_km=50.0)
        # Only Chicago stations should be within 50 km
        assert all(r.station.state == "IL" for r in results)

    def test_country_filter(self) -> None:
        idx = StationIndex.from_stations(_fixture_stations())
        results = idx.nearest(51.50, -0.10, country="GBR", limit=10)
        assert all(r.station.country == "GBR" for r in results)

    def test_results_sorted_by_distance(self) -> None:
        idx = StationIndex.from_stations(_fixture_stations())
        results = idx.nearest(45.0, -75.0, limit=5)
        distances = [r.distance_km for r in results]
        assert distances == sorted(distances)


class TestFilter:
    def test_filter_by_country(self) -> None:
        idx = StationIndex.from_stations(_fixture_stations())
        results = idx.filter(country="USA")
        assert len(results) == 3
        assert all(s.country == "USA" for s in results)

    def test_filter_by_state(self) -> None:
        idx = StationIndex.from_stations(_fixture_stations())
        results = idx.filter(state="IL")
        assert len(results) == 2

    def test_filter_combined(self) -> None:
        idx = StationIndex.from_stations(_fixture_stations())
        results = idx.filter(country="USA", state="NY")
        assert len(results) == 1
        assert results[0].wmo == 744860

    def test_countries(self) -> None:
        idx = StationIndex.from_stations(_fixture_stations())
        assert idx.countries == ["FRA", "GBR", "USA"]
