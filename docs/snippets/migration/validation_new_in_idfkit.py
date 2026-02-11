from idfkit import validate_document

result = validate_document(doc)
if not result.is_valid:
    for error in result.errors:
        print(error)
