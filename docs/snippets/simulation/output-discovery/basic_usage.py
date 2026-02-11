from idfkit.simulation import simulate

result = simulate(model, weather)

variables = result.variables
if variables is not None:
    # Search for temperature-related outputs
    matches = variables.search("Temperature")
    for var in matches[:10]:
        print(f"{var.name} [{var.units}]")
