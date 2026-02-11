location = ddm.location
if location:
    print(f"Site: {location.name}")
    print(f"Latitude: {location.latitude}")
    print(f"Longitude: {location.longitude}")
    print(f"Time Zone: {location.time_zone}")
    print(f"Elevation: {location.elevation} m")
