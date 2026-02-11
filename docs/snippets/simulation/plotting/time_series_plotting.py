ts = result.sql.get_timeseries(
    "Zone Mean Air Temperature",
    "ZONE 1",
)

# Default plot
fig = ts.plot()

# Custom title
fig = ts.plot(title="My Custom Title")

# Explicit backend
from idfkit.simulation import MatplotlibBackend

fig = ts.plot(backend=MatplotlibBackend())
