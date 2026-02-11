from idfkit import load_idf
from idfkit.weather import (
    StationIndex,
    WeatherDownloader,
    DesignDayManager,
    geocode,
)

# Load model
model = load_idf("building.idf")

# Find nearest station
index = StationIndex.load()
lat, lon = geocode("123 Main St, Chicago, IL")
station = index.nearest(lat, lon)[0].station

# Download weather files
downloader = WeatherDownloader()
files = downloader.download(station)

# Apply design days
ddm = DesignDayManager(files.ddy)
added = ddm.apply_to_model(
    model,
    heating="99.6%",
    cooling="1%",
    include_wet_bulb=True,
    update_location=True,
)

print(f"Added {len(added)} design days")
print(f"Location: {model['Site:Location'].values()[0].name}")
