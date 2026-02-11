from idfkit.simulation import simulate

result = simulate(model, weather)

sql = result.sql
if sql is not None:
    # Query data...
