# By name pattern
temp_vars = [v for v in variables if "Temperature" in v.name]

# By key
zone1_vars = [v for v in variables if v.key_value == "ZONE 1"]
