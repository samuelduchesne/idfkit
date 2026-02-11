# Query results once, process locally
result = SimulationResult.from_directory("run-001", fs=fs)

# This downloads the SQL file
sql = result.sql

# Multiple queries are local (file is cached)
ts1 = sql.get_timeseries("Zone Mean Air Temperature", "ZONE 1")
ts2 = sql.get_timeseries("Zone Air Relative Humidity", "ZONE 1")
