if not result.success:
    print(errors.summary())
    for err in errors.fatal + errors.severe:
        print(err.message)
