from idfkit.simulation import simulate_batch, SimulationCache

cache = SimulationCache()

# Safe: all workers share the cache
batch = simulate_batch(jobs, max_workers=8, cache=cache)
