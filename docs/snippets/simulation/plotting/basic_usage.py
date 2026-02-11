from idfkit.simulation import MatplotlibBackend

backend = MatplotlibBackend()
fig = backend.line(
    x=list(ts.timestamps),
    y=list(ts.values),
    title="Zone Temperature",
    xlabel="Time",
    ylabel="Temperature (°C)",
)

# Save to file
fig.savefig("temperature.png")
