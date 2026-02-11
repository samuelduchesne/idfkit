from idfkit.weather import StationIndex, geocode

index = StationIndex.load()

# One-liner using splat operator
results = index.nearest(*geocode("Willis Tower, Chicago, IL"))

# First result is the nearest station
station = results[0].station
print(f"Nearest: {station.display_name} ({results[0].distance_km:.1f} km)")
