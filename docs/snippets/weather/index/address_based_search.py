from idfkit.weather import StationIndex, geocode

index = StationIndex.load()
results = index.nearest(*geocode("350 Fifth Avenue, New York, NY"))

for r in results[:3]:
    print(f"{r.station.display_name}: {r.distance_km:.0f} km")
