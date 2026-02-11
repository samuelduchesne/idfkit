result = simulate(model, weather)

if not result.success:
    print(f"Exit code: {result.exit_code}")

    # Check errors
    if result.errors.has_fatal:
        for err in result.errors.fatal:
            print(f"Fatal: {err.message}")
