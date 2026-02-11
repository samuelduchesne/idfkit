result = simulate(model, weather)  # Just runs EnergyPlus
result.errors  # Parses ERR file on first access
result.sql  # Opens SQLite database on first access
