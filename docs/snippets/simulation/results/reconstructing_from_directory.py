from idfkit.simulation import SimulationResult

# From a local directory
result = SimulationResult.from_directory("/path/to/sim_output")

# From a cloud storage location
from idfkit.simulation import S3FileSystem

fs = S3FileSystem(bucket="my-bucket")
result = SimulationResult.from_directory("runs/run-001", fs=fs)

# Query data
ts = result.sql.get_timeseries("Zone Mean Air Temperature", "ZONE 1")
