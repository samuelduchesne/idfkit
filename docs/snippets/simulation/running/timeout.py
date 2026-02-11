try:
    result = simulate(model, weather, timeout=60.0)  # 1 minute max
except SimulationError as e:
    if e.exit_code is None:
        print("Simulation timed out")
