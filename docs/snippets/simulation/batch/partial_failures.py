if not batch.all_succeeded:
    failed_count = len(batch.failed)
    print(f"{failed_count} jobs failed")

    # Process only successful results
    for result in batch.succeeded:
        # ... analyze results
