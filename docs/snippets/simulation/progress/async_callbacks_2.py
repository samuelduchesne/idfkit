# This works too -- no need to make it async for simple logging
result = await async_simulate(model, "weather.epw", on_progress=lambda e: print(e.phase))
