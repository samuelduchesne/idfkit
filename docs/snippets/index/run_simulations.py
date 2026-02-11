from idfkit.simulation import simulate

result = simulate(doc, "weather.epw", design_day=True)

# Query results
ts = result.sql.get_timeseries(
    variable_name="Zone Mean Air Temperature",
    key_value="Office",
)
print(f"Max temp: {max(ts.values):.1f}")
