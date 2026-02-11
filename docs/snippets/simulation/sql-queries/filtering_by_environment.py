# Design day results only (use for design_day=True simulations)
ts = sql.get_timeseries(
    "Zone Mean Air Temperature",
    "ZONE 1",
    environment="sizing",
)

# Annual/run period results only (default)
ts = sql.get_timeseries(
    "Zone Mean Air Temperature",
    "ZONE 1",
    environment="annual",
)

# All environments (design days + run periods)
ts = sql.get_timeseries(
    "Zone Mean Air Temperature",
    "ZONE 1",
    environment=None,
)
