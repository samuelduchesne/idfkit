# All output variables
for var in variables.variables:
    print(f"Variable: {var.name} [{var.units}]")

# All meters
for meter in variables.meters:
    print(f"Meter: {meter.name} [{meter.units}]")
