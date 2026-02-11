from idfkit.simulation import simulate_batch, SimulationJob

# Create jobs
jobs = [
    SimulationJob(model=model1, weather="weather.epw", label="baseline"),
    SimulationJob(model=model2, weather="weather.epw", label="improved"),
]

# Run in parallel
batch = simulate_batch(jobs, max_workers=4)

print(f"Completed: {len(batch.succeeded)}/{len(batch)}")
for i, result in enumerate(batch):
    print(f"  Job {i}: {'Success' if result.success else 'Failed'}")
