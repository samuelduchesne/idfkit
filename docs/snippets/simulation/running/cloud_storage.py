from idfkit.simulation import S3FileSystem

fs = S3FileSystem(bucket="my-bucket", prefix="runs/")
result = simulate(
    model,
    weather,
    output_dir="run-001",  # Required with fs
    fs=fs,
)
