# All classified annual design days (returns a list of IDFObject)
for dd_obj in ddm.annual:
    print(dd_obj.name)

# Monthly design days
for dd_obj in ddm.monthly:
    print(dd_obj.name)
