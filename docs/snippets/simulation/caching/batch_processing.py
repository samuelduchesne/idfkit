from idfkit.simulation import simulate_batch, SimulationCache

cache = SimulationCache()

# All jobs share the same cache
batch1 = simulate_batch(jobs, cache=cache)

# Re-running unchanged jobs hits cache
batch2 = simulate_batch(jobs, cache=cache)  # Instant for unchanged
