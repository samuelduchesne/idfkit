errors = result.errors

# Summary
print(errors.summary())

# Check for fatal errors
if errors.has_fatal:
    for err in errors.fatal:
        print(f"FATAL: {err.message}")

# Check for severe errors
if errors.has_severe:
    for err in errors.severe:
        print(f"SEVERE: {err.message}")

# All warnings
for warn in errors.warnings:
    print(f"Warning: {warn.message}")

# Counts
print(f"Fatal: {errors.fatal_count}")
print(f"Severe: {errors.severe_count}")
print(f"Warnings: {errors.warning_count}")
