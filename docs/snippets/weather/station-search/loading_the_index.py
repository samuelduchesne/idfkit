from idfkit.weather import StationIndex

# Instant load from bundled data (no network needed)
index = StationIndex.load()

print(f"Stations: {len(index)}")
print(f"Countries: {len(index.countries)}")
