# Search first, review, then add selectively
matches = variables.search("Heating")

# Filter to specific ones
selected = [v for v in matches if "Coil" in v.name]

# Add to model (name is optional for Output:Variable)
for var in selected:
    model.add(
        "Output:Variable",
        key_value="*",
        variable_name=var.name,
        reporting_frequency="Timestep",
    )
