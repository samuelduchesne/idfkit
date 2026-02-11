from idfkit.simulation import SimulationJob, S3FileSystem

fs = S3FileSystem(bucket="simulations", prefix="study-001/")

jobs = [
    SimulationJob(
        model=variant,
        weather="weather.epw",
        label=f"case-{i}",
        output_dir=f"case-{i}",
        fs=fs,
    )
    for i, variant in enumerate(variants)
]
