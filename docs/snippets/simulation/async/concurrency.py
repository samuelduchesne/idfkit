# Use all CPUs (default)
batch = await async_simulate_batch(jobs)

# Limit to 4 concurrent simulations
batch = await async_simulate_batch(jobs, max_concurrent=4)

# Sequential (useful for debugging)
batch = await async_simulate_batch(jobs, max_concurrent=1)
