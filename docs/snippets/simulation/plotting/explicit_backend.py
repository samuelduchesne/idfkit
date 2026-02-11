from idfkit.simulation import MatplotlibBackend, PlotlyBackend

# Force matplotlib
fig = ts.plot(backend=MatplotlibBackend())

# Force plotly
fig = ts.plot(backend=PlotlyBackend())
