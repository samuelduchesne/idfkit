from idfkit.weather import apply_ashrae_sizing

# Apply ASHRAE 90.1 design conditions
added = apply_ashrae_sizing(model, station, standard="90.1")
print(f"Added {len(added)} design days")
