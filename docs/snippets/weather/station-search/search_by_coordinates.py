# Nearest to downtown Chicago
results = index.nearest(41.88, -87.63)

for r in results[:5]:
    print(f"{r.station.display_name}: {r.distance_km:.1f} km")
