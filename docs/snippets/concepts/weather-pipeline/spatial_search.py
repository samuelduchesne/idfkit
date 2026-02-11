# Find nearest stations to a coordinate
results = index.nearest(41.88, -87.63, limit=5)

for r in results:
    print(f"{r.station.display_name}: {r.distance_km:.1f} km")
