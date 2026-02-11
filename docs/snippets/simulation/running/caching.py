from idfkit.simulation import SimulationCache

cache = SimulationCache()

# First run: executes simulation
result1 = simulate(model, weather, cache=cache)

# Second run: instant cache hit
result2 = simulate(model, weather, cache=cache)
