from idfkit.weather import StationIndex, geocode

# Load the station index (instant, no network needed)
index = StationIndex.load()

# Search by name
results = index.search("chicago ohare")
print(results[0].station.display_name)

# Find nearest station to an address
results = index.nearest(*geocode("Willis Tower, Chicago, IL"))
station = results[0].station
print(f"{station.display_name}: {results[0].distance_km:.0f} km away")
