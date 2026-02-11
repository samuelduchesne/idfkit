from idfkit.simulation import simulate_batch, SimulationJob

jobs = [SimulationJob(model=variant, weather="weather.epw", label=f"case-{i}") for i, variant in enumerate(variants)]
batch = simulate_batch(jobs, max_workers=4)
