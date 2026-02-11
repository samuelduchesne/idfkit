import asyncio
from idfkit.simulation import async_simulate_batch_stream, SimulationJob


async def main():
    jobs = [
        SimulationJob(model=variant, weather="weather.epw", label=f"case-{i}") for i, variant in enumerate(variants)
    ]

    # Collect events and reorder by original index
    results = [None] * len(jobs)
    async for event in async_simulate_batch_stream(jobs, max_concurrent=4):
        results[event.index] = event.result
        pct = event.completed / event.total * 100
        print(f"[{pct:3.0f}%] {event.label}: {'OK' if event.result.success else 'FAIL'}")

    # Results are now in submission order
    for i, result in enumerate(results):
        if result.success:
            ts = result.sql.get_timeseries("Zone Mean Air Temperature", "ZONE 1")
            print(f"Case {i}: max temp {max(ts.values):.1f}°C")


asyncio.run(main())
