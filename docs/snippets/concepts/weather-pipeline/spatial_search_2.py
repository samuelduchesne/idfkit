from idfkit.weather import geocode

lat, lon = geocode("350 Fifth Avenue, New York, NY")
results = index.nearest(lat, lon)
