# Multiple entries can have the same WMO
results = index.search("725300")  # Chicago O'Hare WMO
for r in results:
    print(f"{r.station.source_data}: {r.station.url}")
