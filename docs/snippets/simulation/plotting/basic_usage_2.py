from idfkit.simulation import PlotlyBackend

backend = PlotlyBackend()
fig = backend.line(
    x=list(ts.timestamps),
    y=list(ts.values),
    title="Zone Temperature",
)

# Interactive display
fig.show()

# Save to HTML
fig.write_html("temperature.html")
