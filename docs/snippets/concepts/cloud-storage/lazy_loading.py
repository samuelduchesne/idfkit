result = SimulationResult.from_directory("run-001", fs=s3_fs)

# Nothing downloaded yet
# ...

# Downloads only the SQLite file
ts = result.sql.get_timeseries(...)
