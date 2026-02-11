from idfkit.exceptions import SimulationError

try:
    result = simulate(model, weather)
except SimulationError as e:
    print(f"Simulation failed: {e}")
    print(f"Exit code: {e.exit_code}")
    print(f"Stderr: {e.stderr}")
