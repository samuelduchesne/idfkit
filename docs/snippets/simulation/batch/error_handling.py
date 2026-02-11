batch = simulate_batch(jobs)

for i, result in enumerate(batch):
    if not result.success:
        print(f"Job {i} failed:")
        print(f"  Exit code: {result.exit_code}")
        print(f"  Stderr: {result.stderr}")
        for err in result.errors.fatal:
            print(f"  Error: {err.message}")
