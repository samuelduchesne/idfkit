errors = result.errors

# Fatal errors (simulation stopped)
for err in errors.fatal:
    print(f"FATAL: {err.message}")

# Severe errors (may cause incorrect results)
for err in errors.severe:
    print(f"SEVERE: {err.message}")

# Warnings
for warn in errors.warnings:
    print(f"Warning: {warn.message}")
