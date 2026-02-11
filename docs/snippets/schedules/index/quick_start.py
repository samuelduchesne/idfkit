from datetime import datetime
from idfkit import load_idf
from idfkit.schedules import evaluate, values

# Load a model
doc = load_idf("building.idf")

# Get a schedule by name
schedule = doc["Schedule:Compact"]["Office Occupancy"]

# Evaluate at a specific time
value = evaluate(schedule, datetime(2024, 1, 8, 10, 0), document=doc)
print(f"Value at Monday 10am: {value}")

# Get hourly values for a full year
hourly = values(schedule, year=2024, document=doc)
print(f"Annual hours: {len(hourly)}")  # 8784 for leap year
