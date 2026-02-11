from idfkit import load_idf
from idfkit.simulation import simulate, S3FileSystem

# Create S3-backed filesystem
fs = S3FileSystem(
    bucket="my-simulations",
    prefix="project-x/",
)

# Run simulation with S3 storage
model = load_idf("building.idf")
result = simulate(
    model,
    "weather.epw",
    output_dir="run-001",  # Required with fs
    fs=fs,
)

# Results are now in s3://my-simulations/project-x/run-001/
print(f"Results stored at: {result.run_dir}")
