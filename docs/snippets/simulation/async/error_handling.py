from idfkit.exceptions import SimulationError

try:
    result = await async_simulate(model, weather, timeout=60)
except SimulationError as e:
    if e.exit_code is None:
        print("Simulation timed out")
    else:
        print(f"Failed: {e}")
