result = simulate(model, weather)

if not result.success:
    print(f"Exit code: {result.exit_code}")
    print(f"Stderr: {result.stderr}")
    for err in result.errors.fatal:
        print(f"Error: {err.message}")
