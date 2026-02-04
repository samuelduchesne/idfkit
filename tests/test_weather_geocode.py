"""Tests for idfkit.weather.geocode (mocked, no network)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from idfkit.weather.geocode import geocode


def _mock_response(data: bytes) -> MagicMock:
    mock_resp = MagicMock()
    mock_resp.read.return_value = data
    mock_resp.__enter__ = MagicMock(return_value=mock_resp)
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


class TestGeocode:
    @patch("urllib.request.urlopen")
    @patch("idfkit.weather.geocode._last_request_time", 0.0)
    @patch("idfkit.weather.geocode.time")
    def test_successful_geocode(self, mock_time: MagicMock, mock_urlopen: MagicMock) -> None:
        mock_time.monotonic.return_value = 100.0
        mock_time.sleep = MagicMock()

        response_data = [{"lat": "41.8781", "lon": "-87.6298", "display_name": "Chicago"}]
        mock_urlopen.return_value = _mock_response(json.dumps(response_data).encode())

        result = geocode("Willis Tower, Chicago, IL")

        assert result is not None
        lat, lon = result
        assert abs(lat - 41.8781) < 0.001
        assert abs(lon - (-87.6298)) < 0.001

    @patch("urllib.request.urlopen")
    @patch("idfkit.weather.geocode._last_request_time", 0.0)
    @patch("idfkit.weather.geocode.time")
    def test_empty_response_returns_none(self, mock_time: MagicMock, mock_urlopen: MagicMock) -> None:
        mock_time.monotonic.return_value = 100.0
        mock_time.sleep = MagicMock()
        mock_urlopen.return_value = _mock_response(b"[]")

        result = geocode("zzzznonexistentplace")
        assert result is None

    @patch("urllib.request.urlopen")
    @patch("idfkit.weather.geocode._last_request_time", 0.0)
    @patch("idfkit.weather.geocode.time")
    def test_network_error_returns_none(self, mock_time: MagicMock, mock_urlopen: MagicMock) -> None:
        mock_time.monotonic.return_value = 100.0
        mock_time.sleep = MagicMock()

        from urllib.error import URLError

        mock_urlopen.side_effect = URLError("Network unreachable")

        result = geocode("Chicago, IL")
        assert result is None
