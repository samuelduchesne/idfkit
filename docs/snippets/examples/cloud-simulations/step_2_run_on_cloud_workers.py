# worker.py (runs on AWS Batch, Kubernetes, etc.)
from idfkit.simulation import simulate, S3FileSystem

fs = S3FileSystem(bucket="simulations", prefix="study-001/")

# Run single job
result = simulate(
    model,
    weather_path,  # Must be local
    output_dir=f"case-{job_id}",
    fs=fs,
)

# Results uploaded to S3 automatically
