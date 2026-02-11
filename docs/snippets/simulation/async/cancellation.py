async def run_with_timeout():
    task = asyncio.create_task(async_simulate(model, "weather.epw"))

    try:
        result = await asyncio.wait_for(task, timeout=120)
    except asyncio.TimeoutError:
        print("Simulation cancelled after 120s")
