from idfkit.simulation import simulate_batch, SimulationJob

jobs = [
    SimulationJob(model=variant1, weather="weather.epw", label="case-1"),
    SimulationJob(model=variant2, weather="weather.epw", label="case-2"),
]

batch = simulate_batch(jobs, max_workers=4)
