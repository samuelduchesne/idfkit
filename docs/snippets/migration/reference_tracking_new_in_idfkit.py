# Find every object that points to the "Office" zone
for obj in doc.get_referencing("Office"):
    print(obj.obj_type, obj.name)

# Find every name that the People object references
names = doc.get_references(people_obj)
