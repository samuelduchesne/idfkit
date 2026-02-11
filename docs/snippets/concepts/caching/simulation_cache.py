from idfkit.simulation import simulate, SimulationCache

cache = SimulationCache()

# First run: executes EnergyPlus
result1 = simulate(model, weather, cache=cache)

# Second run: instant cache hit
result2 = simulate(model, weather, cache=cache)
