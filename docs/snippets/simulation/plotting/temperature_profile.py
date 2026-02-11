from idfkit.simulation import plot_temperature_profile

fig = plot_temperature_profile(
    result,
    zone_name="THERMAL ZONE 1",
    title="Zone Temperatures",
)
