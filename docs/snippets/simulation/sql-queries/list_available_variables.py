variables = sql.list_variables()

for var in variables[:10]:
    print(f"{var.name} ({var.key_value}) [{var.units}] - {var.frequency}")
