from idfkit import load_idf
from idfkit.weather import (
    StationIndex,
    WeatherDownloader,
    DesignDayManager,
    geocode,
)

# Load your model
model = load_idf("building.idf")

# Find nearest station to project location
index = StationIndex.load()
lat, lon = geocode("123 Main St, Chicago, IL")
station = index.nearest(lat, lon)[0].station

# Download weather files
downloader = WeatherDownloader()
files = downloader.download(station)

# Apply design days
ddm = DesignDayManager(files.ddy)
ddm.apply_to_model(
    model,
    heating="99.6%",
    cooling="1%",
    update_location=True,
)

# Now ready for simulation
from idfkit.simulation import simulate

result = simulate(model, files.epw)
