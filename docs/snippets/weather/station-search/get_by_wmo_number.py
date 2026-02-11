# Get specific station by WMO
results = index.get_by_wmo("725300")

for station in results:
    print(f"{station.display_name}: {station.source}")
