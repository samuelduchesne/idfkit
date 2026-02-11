from idfkit.simulation import find_energyplus

config = find_energyplus()
print(f"EnergyPlus {config.version[0]}.{config.version[1]}.{config.version[2]}")
print(f"Executable: {config.executable}")
