sql = result.sql
if sql is None:
    print("No SQL output - was Output:SQLite in the model?")
    return

# Get time series (raises KeyError if not found)
try:
    ts = sql.get_timeseries("Nonexistent Variable", "ZONE 1")
except KeyError as e:
    print(f"Variable not found: {e}")
