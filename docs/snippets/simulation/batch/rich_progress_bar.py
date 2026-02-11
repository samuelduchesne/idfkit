from rich.progress import Progress

with Progress() as progress:
    task = progress.add_task("Simulating...", total=len(jobs))

    def callback(completed, total, label, success):
        progress.update(task, completed=completed)

    batch = simulate_batch(jobs, progress=callback)
