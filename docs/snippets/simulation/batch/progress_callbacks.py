def on_progress(completed, total, label, success):
    status = "OK" if success else "FAIL"
    print(f"[{completed}/{total}] {label}: {status}")


batch = simulate_batch(jobs, progress=on_progress)
