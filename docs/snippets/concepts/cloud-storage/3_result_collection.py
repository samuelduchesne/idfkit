from idfkit.simulation import SimulationResult, S3FileSystem

fs = S3FileSystem(bucket="simulations", prefix="study-001/")

# Reconstruct result from S3
result = SimulationResult.from_directory("case-42", fs=fs)

# Query data (transparently reads from S3)
ts = result.sql.get_timeseries("Zone Mean Air Temperature", "ZONE 1")
