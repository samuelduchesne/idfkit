# These are automatically spaced 1 second apart
for address in addresses:
    lat, lon = geocode(address)  # Rate limited internally
    print(f"{address}: {lat:.2f}, {lon:.2f}")
