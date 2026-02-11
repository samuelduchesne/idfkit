from idfkit.simulation import async_simulate_batch_stream

async for event in async_simulate_batch_stream(jobs, max_concurrent=4):
    print(f"[{event.completed}/{event.total}] {event.label}")
