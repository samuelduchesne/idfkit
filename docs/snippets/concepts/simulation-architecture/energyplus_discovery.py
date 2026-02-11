from idfkit.simulation import find_energyplus

config = find_energyplus()
print(f"Version: {config.version}")
print(f"Path: {config.executable}")
