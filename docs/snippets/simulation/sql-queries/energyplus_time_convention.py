ts = sql.get_timeseries("Zone Mean Air Temperature", "ZONE 1")

# Timestamps are proper Python datetime objects
first = ts.timestamps[0]
print(f"Year: {first.year}")  # 2017 (reference year)
print(f"Month: {first.month}")
print(f"Day: {first.day}")
print(f"Hour: {first.hour}")
