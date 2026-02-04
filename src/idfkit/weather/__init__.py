"""Weather station search, download, and design day injection.

This sub-package provides tools for:

* **Searching** the climate.onebuilding.org TMYx station index by name,
  coordinates, or metadata filters.
* **Downloading** EPW and DDY weather files with local caching.
* **Parsing** DDY files and injecting ASHRAE design day conditions into
  EnergyPlus models.
* **Geocoding** addresses to coordinates via the free Nominatim API.

Quick start::

    from idfkit.weather import StationIndex, WeatherDownloader, apply_ashrae_sizing

    index = StationIndex.load()
    results = index.search("chicago ohare")
    station = results[0].station

    downloader = WeatherDownloader()
    files = downloader.download(station)
    print(files.epw, files.ddy)

Requires ``openpyxl`` for station index loading.  Install with::

    pip install idfkit[weather]
"""

from __future__ import annotations

from .designday import DesignDayManager, DesignDayType, apply_ashrae_sizing
from .download import WeatherDownloader, WeatherFiles
from .geocode import geocode
from .index import StationIndex
from .station import SearchResult, SpatialResult, WeatherStation

__all__ = [
    "DesignDayManager",
    "DesignDayType",
    "SearchResult",
    "SpatialResult",
    "StationIndex",
    "WeatherDownloader",
    "WeatherFiles",
    "WeatherStation",
    "apply_ashrae_sizing",
    "geocode",
]
