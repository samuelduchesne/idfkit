# No caching
result = simulate(model, weather)

# With caching
result = simulate(model, weather, cache=SimulationCache())
