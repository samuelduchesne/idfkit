from idfkit import load_idf
from idfkit.schedules import values, to_series

doc = load_idf("office.idf")
occupancy = doc["Schedule:Compact"]["BLDG_OCC_SCH"]

# Get annual values
annual = values(occupancy, year=2024, document=doc)

# Basic statistics
total_hours = len([v for v in annual if v > 0])
print(f"Occupied hours: {total_hours}")

# Peak analysis with pandas
series = to_series(occupancy, year=2024, document=doc)
print(f"Peak occupancy: {series.max()}")
print(f"Average (occupied): {series[series > 0].mean():.2f}")

# Weekly pattern
weekly = series.groupby(series.index.dayofweek).mean()
print("Average by day of week:")
print(weekly)
