from idfkit.weather import StationIndex, WeatherDownloader

# Load station index (instant, no network needed)
index = StationIndex.load()
print(f"{len(index)} stations from {len(index.countries)} countries")

# Search by name
results = index.search("chicago ohare")
station = results[0].station
print(f"Found: {station.display_name}")

# Download weather files
downloader = WeatherDownloader()
files = downloader.download(station)
print(f"EPW: {files.epw}")
print(f"DDY: {files.ddy}")
