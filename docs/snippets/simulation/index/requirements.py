from idfkit.simulation import find_energyplus

config = find_energyplus()
print(f"Found EnergyPlus {config.version[0]}.{config.version[1]}")
