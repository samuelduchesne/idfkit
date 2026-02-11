# Geocoding

The `geocode()` function converts addresses to coordinates using the free
Nominatim (OpenStreetMap) service.

## Basic Usage

```python
--8<-- "docs/snippets/weather/geocoding/basic_usage.py:example"
```

## With Station Search

Combine with `StationIndex.nearest()` for address-based weather station lookup:

```python
--8<-- "docs/snippets/weather/geocoding/with_station_search.py:example"
```

## Address Formats

The geocoder accepts various address formats:

```python
--8<-- "docs/snippets/weather/geocoding/address_formats.py:example"
```

## Error Handling

```python
--8<-- "docs/snippets/weather/geocoding/error_handling.py:example"
```

### Common Errors

| Situation | Behavior |
|-----------|----------|
| Address not found | Raises `GeocodingError` |
| Network error | Raises `GeocodingError` |
| Rate limited | Automatically retries with delay |

## Rate Limiting

Nominatim requires a maximum of 1 request per second. The `geocode()`
function automatically handles rate limiting:

```python
--8<-- "docs/snippets/weather/geocoding/rate_limiting.py:example"
```

## No API Key Required

Nominatim is a free service that doesn't require an API key. However:

- Be respectful of usage limits
- Avoid bulk geocoding (use batch geocoding services for large datasets)
- Cache results when possible

## Caching Results

For repeated lookups, cache the coordinates:

```python
--8<-- "docs/snippets/weather/geocoding/caching_results.py:example"
```

## Complete Workflow

```python
--8<-- "docs/snippets/weather/geocoding/complete_workflow.py:example"
```

## Accuracy Notes

- Geocoding accuracy varies by location and address specificity
- Results may vary slightly over time as OpenStreetMap data is updated
- For critical applications, verify coordinates manually

## Alternative: Direct Coordinates

If you already know the coordinates, skip geocoding entirely:

```python
--8<-- "docs/snippets/weather/geocoding/alternative_direct_coordinates.py:example"
```

## See Also

- [Station Search](station-search.md) — Find weather stations
- [Weather Downloads](downloads.md) — Download weather files
- [Weather Overview](index.md) — Module overview
