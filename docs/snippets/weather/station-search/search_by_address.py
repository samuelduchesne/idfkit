from idfkit.weather import StationIndex, geocode

index = StationIndex.load()

# One-liner using splat operator
results = index.nearest(*geocode("Willis Tower, Chicago, IL"))

# Or step by step
lat, lon = geocode("350 Fifth Avenue, New York, NY")
results = index.nearest(lat, lon)
