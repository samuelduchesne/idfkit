from idfkit.simulation import SimulationCache, S3FileSystem

cache = SimulationCache()
fs = S3FileSystem(bucket="my-bucket", prefix="study/")

result = await async_simulate(
    model, "weather.epw",
    cache=cache,
    output_dir="run-001",
    fs=fs,
)
