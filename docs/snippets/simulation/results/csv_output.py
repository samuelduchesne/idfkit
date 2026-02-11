csv_result = result.csv
if csv_result is not None:
    # List all columns
    for col in csv_result.columns:
        print(f"{col.variable_name} ({col.key_value}) [{col.units}]")

    # Get data for a specific column
    values = csv_result.get_column_values("Zone Mean Air Temperature")
