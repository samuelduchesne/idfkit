from idfkit.simulation import SimulationResult, S3FileSystem

fs = S3FileSystem(bucket="simulations", prefix="study-001/")

# Reconstruct results
results = []
for i in range(num_cases):
    result = SimulationResult.from_directory(f"case-{i:04d}", fs=fs)
    results.append(result)

# Analyze
for i, result in enumerate(results):
    ts = result.sql.get_timeseries(
        "Zone Mean Air Temperature",
        "ZONE 1",
    )
    print(f"Case {i}: max temp = {max(ts.values):.1f}°C")
