obj.getrange("Density")
# {'minimum': 0, 'type': 'real'}

obj.checkrange("Density")  # raises RangeError if out of range
