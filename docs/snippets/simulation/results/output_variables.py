variables = result.variables
if variables is not None:
    # Search for variables
    matches = variables.search("Temperature")
    for var in matches:
        print(f"{var.name} [{var.units}]")

    # Add outputs to model for next run
    variables.add_all_to_model(model, filter_pattern="Zone.*Temperature")
