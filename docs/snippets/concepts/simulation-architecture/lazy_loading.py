result = simulate(model, weather)  # Fast: just runs EnergyPlus

# These are lazy — parsed on first access:
result.errors  # Parses ERR file
result.sql  # Opens SQLite database
result.variables  # Parses RDD file
