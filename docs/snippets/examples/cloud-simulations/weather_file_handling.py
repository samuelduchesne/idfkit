from idfkit.weather import StationIndex, WeatherDownloader

# Download weather file locally
index = StationIndex.load()
station = index.search("chicago")[0].station
downloader = WeatherDownloader()
files = downloader.download(station)

# Then use local weather with S3 output
fs = S3FileSystem(bucket="results", prefix="study/")
result = simulate(
    model,
    files.epw,  # Local path
    output_dir="run-001",
    fs=fs,
)
