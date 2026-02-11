try:
    result = simulate(model, weather, timeout=60.0)
except SimulationError as e:
    if e.exit_code is None:
        print("Simulation timed out")
    else:
        print(f"Simulation failed with exit code {e.exit_code}")
