from idfkit.weather import StationIndex

index = StationIndex.load()  # Instant, no network
print(f"{len(index)} entries, {len(index.countries)} countries")
