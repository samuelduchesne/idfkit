from idfkit.simulation import simulate

result = simulate(model, weather)

# Access the error report
errors = result.errors

# Check for problems
if errors.has_fatal:
    print("Simulation had fatal errors")
if errors.has_severe:
    print("Simulation had severe errors")
if errors.warning_count > 0:
    print(f"Simulation had {errors.warning_count} warnings")
