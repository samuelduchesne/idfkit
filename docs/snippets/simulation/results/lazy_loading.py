result = simulate(model, weather)

# Nothing parsed yet - only metadata stored

result.errors  # NOW parses .err file
result.sql  # NOW opens SQLite database
result.variables  # NOW parses .rdd/.mdd files
result.html  # NOW parses HTML tabular output
