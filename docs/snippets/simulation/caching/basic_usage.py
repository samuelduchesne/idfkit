from idfkit.simulation import simulate, SimulationCache

cache = SimulationCache()

# First run: executes EnergyPlus
result1 = simulate(model, "weather.epw", cache=cache)
print(f"Runtime: {result1.runtime_seconds:.1f}s")

# Second run: instant cache hit
result2 = simulate(model, "weather.epw", cache=cache)
print(f"Runtime: {result2.runtime_seconds:.1f}s")  # Near zero
