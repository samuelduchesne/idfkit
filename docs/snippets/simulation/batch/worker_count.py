# Use all CPUs
batch = simulate_batch(jobs, max_workers=None)  # Default

# Limit to 4 concurrent simulations
batch = simulate_batch(jobs, max_workers=4)

# Sequential (useful for debugging)
batch = simulate_batch(jobs, max_workers=1)
