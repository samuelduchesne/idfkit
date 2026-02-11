from idfkit.simulation import SimulationCache

cache = SimulationCache()

# All jobs share the same cache
batch = simulate_batch(jobs, cache=cache)

# Re-running is instant for unchanged models
batch2 = simulate_batch(jobs, cache=cache)  # Cache hits
