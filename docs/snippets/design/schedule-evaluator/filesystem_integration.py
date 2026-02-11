from idfkit import load_idf
from idfkit.simulation.fs import S3FileSystem
from idfkit.schedules import values

# Load model from S3
fs = S3FileSystem(bucket="models", prefix="building-42/")
model = load_idf("model.idf")  # Local IDF

# Evaluate Schedule:File that references CSV on S3
schedule = model.get_schedule("External Occupancy")
hourly = values(schedule, fs=fs)  # Reads CSV from S3
