from idfkit.simulation import simulate, S3FileSystem, SimulationProgress

fs = S3FileSystem(bucket="my-bucket", prefix="runs/")


def on_progress(event: SimulationProgress) -> None:
    # This fires during local execution, before upload
    print(f"{event.phase}: {event.percent}")


result = simulate(
    model,
    "weather.epw",
    output_dir="run-001",
    fs=fs,
    on_progress=on_progress,
)
