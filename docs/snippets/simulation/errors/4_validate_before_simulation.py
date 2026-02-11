from idfkit import validate_document

validation = validate_document(model)
if not validation.is_valid:
    for err in validation.errors:
        print(err)
