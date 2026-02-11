# Auto-discovery
result = simulate(model, weather)

# Explicit path
from idfkit.simulation import find_energyplus

config = find_energyplus("/custom/path/EnergyPlus-24-1-0")
result = simulate(model, weather, energyplus=config)

# Environment variable
# Set ENERGYPLUS_DIR=/path/to/EnergyPlus before running
result = simulate(model, weather)
