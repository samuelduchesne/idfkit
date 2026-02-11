# Get all zones
for zone in model["Zone"]:
    print(f"Zone: {zone.name}")

# Get a specific zone by name
office = model["Zone"]["Office"]
print(f"Origin: ({office.x_origin}, {office.y_origin}, {office.z_origin})")
