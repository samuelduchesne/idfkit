# In your AWS Batch / Kubernetes job:
from idfkit.simulation import simulate, S3FileSystem

fs = S3FileSystem(bucket="simulations", prefix="study-001/")
result = simulate(model, weather, output_dir="case-42", fs=fs)

# Result files are now in s3://simulations/study-001/case-42/
