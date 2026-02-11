batch = simulate_batch(jobs)

# Access results
batch.results  # All results as tuple
batch[0]  # First result (by index)
len(batch)  # Number of jobs

# Filter by success
batch.succeeded  # Only successful results
batch.failed  # Only failed results
batch.all_succeeded  # True if all succeeded

# Timing
print(f"Total time: {batch.total_runtime_seconds:.1f}s")
