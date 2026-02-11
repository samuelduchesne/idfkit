async for event in async_simulate_batch_stream(jobs, max_concurrent=4):
    if not event.result.success:
        print(f"Job {event.label} failed — aborting remaining")
        break  # Remaining tasks are cancelled automatically
