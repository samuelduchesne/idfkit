import asyncio
from idfkit import load_idf
from idfkit.simulation import async_simulate


async def main():
    model = load_idf("building.idf")
    result = await async_simulate(model, "weather.epw", design_day=True)

    print(f"Success: {result.success}")
    print(f"Runtime: {result.runtime_seconds:.1f}s")


asyncio.run(main())
