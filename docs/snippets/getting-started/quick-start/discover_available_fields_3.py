model.add("Zone", "Office", x_orgin=0)  # Raises: unknown field 'x_orgin'

# Disable validation for bulk operations where performance matters
model.add("Zone", "Office", x_origin=0, validate=False)
