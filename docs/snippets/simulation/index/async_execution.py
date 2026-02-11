from idfkit.simulation import async_simulate, async_simulate_batch_stream

# Single simulation
result = await async_simulate(model, "weather.epw")

# Streaming progress
async for event in async_simulate_batch_stream(jobs, max_concurrent=4):
    print(f"[{event.completed}/{event.total}] {event.label}")
