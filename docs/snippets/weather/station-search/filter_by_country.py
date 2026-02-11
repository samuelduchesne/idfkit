# Get all stations in a country
us_stations = index.filter(country="USA")
print(f"US stations: {len(us_stations)}")

# Get all stations in a state/region
california = [s for s in us_stations if s.state == "CA"]
