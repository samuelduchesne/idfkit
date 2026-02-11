from idfkit.simulation import simulate_batch

batch = simulate_batch(jobs)

# Check overall success
if not batch.all_succeeded:
    print(f"{len(batch.failed)} jobs failed")

# Handle failures individually
for i, result in enumerate(batch):
    if not result.success:
        print(f"Job {i} failed:")
        for err in result.errors.fatal:
            print(f"  {err.message}")
