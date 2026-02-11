# No caching — always runs EnergyPlus
result = simulate(model, weather)

# With caching
cache = SimulationCache()
result = simulate(model, weather, cache=cache)
