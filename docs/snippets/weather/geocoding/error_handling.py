from idfkit.weather import geocode, GeocodingError

try:
    lat, lon = geocode("Nonexistent Place XYZ123")
except GeocodingError as e:
    print(f"Geocoding failed: {e}")
