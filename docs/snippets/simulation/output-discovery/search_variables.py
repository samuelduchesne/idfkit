# Search by name pattern
matches = variables.search("Zone Mean Air Temperature")

# Search with regex
matches = variables.search(r"Zone.*Temperature")

# Case-insensitive
matches = variables.search("temperature")  # Finds all temperature vars
