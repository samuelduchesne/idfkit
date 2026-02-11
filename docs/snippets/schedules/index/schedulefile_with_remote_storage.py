from idfkit.simulation.fs import S3FileSystem
from idfkit.schedules import evaluate

# Configure S3 storage
fs = S3FileSystem(bucket="my-bucket", prefix="schedules/")

# Evaluate Schedule:File reading from S3
value = evaluate(schedule, dt, fs=fs, base_path="")
