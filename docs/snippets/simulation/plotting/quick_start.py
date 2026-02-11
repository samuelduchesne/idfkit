from idfkit.simulation import simulate

result = simulate(model, weather)

# Plot time series
ts = result.sql.get_timeseries(
    "Zone Mean Air Temperature",
    "ZONE 1",
)
fig = ts.plot()  # Auto-detects available backend
