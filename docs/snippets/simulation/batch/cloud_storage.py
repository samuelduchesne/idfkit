from idfkit.simulation import S3FileSystem

fs = S3FileSystem(bucket="my-bucket", prefix="study-001/")

# Each job needs an explicit output_dir
jobs = [
    SimulationJob(
        model=variant,
        weather="weather.epw",
        label=f"case-{i}",
        output_dir=f"case-{i}",  # Required with fs
    )
    for i, variant in enumerate(variants)
]

batch = simulate_batch(jobs, fs=fs)
