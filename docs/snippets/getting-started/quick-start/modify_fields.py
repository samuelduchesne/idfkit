# Update a field
office.x_origin = 10.0

# See what references this zone
for obj in model.get_referencing("Office"):
    print(f"  {obj.obj_type}: {obj.name}")
