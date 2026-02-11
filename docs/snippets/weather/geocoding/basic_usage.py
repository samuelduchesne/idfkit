from idfkit.weather import geocode

# Get coordinates for an address
lat, lon = geocode("350 Fifth Avenue, New York, NY")
print(f"Empire State Building: {lat:.4f}, {lon:.4f}")
