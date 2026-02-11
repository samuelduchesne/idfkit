import asyncio
from idfkit.simulation import async_simulate_batch, SimulationJob


async def main():
    jobs = [
        SimulationJob(model=model1, weather="weather.epw", label="baseline"),
        SimulationJob(model=model2, weather="weather.epw", label="improved"),
    ]

    batch = await async_simulate_batch(jobs, max_concurrent=4)

    print(f"Completed: {len(batch.succeeded)}/{len(batch)}")
    for i, result in enumerate(batch):
        print(f"  Job {i}: {'Success' if result.success else 'Failed'}")


asyncio.run(main())
