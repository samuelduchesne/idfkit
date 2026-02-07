# Simulation Progress Tracking

The `on_progress` callback provides real-time visibility into what EnergyPlus
is doing during a simulation.  It fires for warmup iterations, simulation day
changes, post-processing steps, and completion — enabling progress bars, live
logs, and remote monitoring.

## Quick Start

```python
from idfkit import load_idf
from idfkit.simulation import simulate, SimulationProgress

model = load_idf("building.idf")

def on_progress(event: SimulationProgress) -> None:
    if event.percent is not None:
        print(f"[{event.percent:5.1f}%] {event.phase}: {event.message}")
    else:
        print(f"[  ?  ] {event.phase}: {event.message}")

result = simulate(model, "weather.epw", annual=True, on_progress=on_progress)
```

Output:

```
[  ?  ] initializing: Initializing New Environment Parameters
[  ?  ] warmup: Warming up {1}
[  ?  ] warmup: Warming up {2}
[  ?  ] warmup: Warmup Complete
[  0.0%] simulating: Starting Simulation at 01/01/2017 for AnnualRun from 01/01/2017 to 12/31/2017
[  8.5%] simulating: Continuing Simulation at 02/01/2017 for AnnualRun
[ 16.2%] simulating: Continuing Simulation at 03/01/2017 for AnnualRun
...
[ 91.5%] simulating: Continuing Simulation at 12/01/2017 for AnnualRun
[  ?  ] postprocessing: Writing tabular output file results using comma format.
[100.0%] complete: EnergyPlus Completed Successfully.
```

## SimulationProgress

Each callback invocation receives a `SimulationProgress` event:

| Field | Type | Description |
|-------|------|-------------|
| `phase` | `str` | `"initializing"`, `"warmup"`, `"simulating"`, `"postprocessing"`, or `"complete"` |
| `message` | `str` | Raw EnergyPlus stdout line (stripped) |
| `percent` | `float \| None` | Estimated 0–100 completion, or `None` when indeterminate |
| `environment` | `str \| None` | Current simulation environment name |
| `warmup_day` | `int \| None` | Current warmup iteration (1-based) |
| `sim_day` | `int \| None` | Current day-of-year (1-based) |
| `sim_total_days` | `int \| None` | Total simulation days when known |
| `job_index` | `int \| None` | Batch job index (only set in batch mode) |
| `job_label` | `str \| None` | Batch job label (only set in batch mode) |

### Simulation Phases

| Phase | When | `percent` |
|-------|------|-----------|
| `initializing` | EnergyPlus starts a new environment | `None` |
| `warmup` | Iterating warmup days until convergence | `None` |
| `simulating` | Stepping through the simulation period | `float` when period is known |
| `postprocessing` | Writing output files | `None` |
| `complete` | Simulation finished successfully | `100.0` |

### Percentage Estimation

The `percent` field is estimated from the current simulation date relative to
the run period.  It is only available during the `simulating` phase when
EnergyPlus reports the simulation period (e.g. annual runs).

When the period cannot be determined (design-day runs, custom periods without
date ranges), `percent` is `None`.  Your progress indicator should handle this
with a spinner or indeterminate bar.

## Async Callbacks

`async_simulate()` accepts both sync and async callables:

```python
import asyncio
from idfkit.simulation import async_simulate, SimulationProgress

async def on_progress(event: SimulationProgress) -> None:
    """Async callback — awaited by the runner."""
    await websocket.send_json({
        "phase": event.phase,
        "percent": event.percent,
        "message": event.message,
    })

async def main():
    result = await async_simulate(model, "weather.epw", on_progress=on_progress)
```

Synchronous callbacks also work in the async runner and are called directly
without awaiting:

```python
# This works too — no need to make it async for simple logging
result = await async_simulate(model, "weather.epw", on_progress=lambda e: print(e.phase))
```

## Progress Bars

### tqdm (Console)

```python
from tqdm import tqdm
from idfkit.simulation import simulate, SimulationProgress

bar = tqdm(total=100, desc="Simulating", unit="%", bar_format="{l_bar}{bar}| {n:.0f}/{total}%")

def on_progress(event: SimulationProgress) -> None:
    if event.percent is not None:
        bar.n = event.percent
        bar.refresh()
    bar.set_postfix_str(event.phase)

result = simulate(model, "weather.epw", annual=True, on_progress=on_progress)
bar.close()
```

### rich (Console)

```python
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from idfkit.simulation import simulate, SimulationProgress

with Progress(
    SpinnerColumn(),
    TextColumn("[bold blue]{task.description}"),
    BarColumn(),
    TextColumn("{task.percentage:>3.0f}%"),
    TextColumn("[dim]{task.fields[phase]}"),
) as progress:
    task = progress.add_task("Simulating", total=100, phase="starting")

    def on_progress(event: SimulationProgress) -> None:
        if event.percent is not None:
            progress.update(task, completed=event.percent, phase=event.phase)
        else:
            progress.update(task, phase=event.phase)

    result = simulate(model, "weather.epw", annual=True, on_progress=on_progress)
```

### Jupyter (ipywidgets)

```python
import ipywidgets as widgets
from IPython.display import display
from idfkit.simulation import simulate, SimulationProgress

bar = widgets.FloatProgress(min=0, max=100, description="Simulating:")
label = widgets.Label(value="Starting...")
display(widgets.HBox([bar, label]))

def on_progress(event: SimulationProgress) -> None:
    if event.percent is not None:
        bar.value = event.percent
    label.value = f"{event.phase}: {event.message[:60]}"

result = simulate(model, "weather.epw", annual=True, on_progress=on_progress)
bar.value = 100
label.value = "Done!"
```

## Live Logging

### Structured Logging

```python
import logging
from idfkit.simulation import simulate, SimulationProgress

logger = logging.getLogger("simulation")

def on_progress(event: SimulationProgress) -> None:
    logger.info(
        "simulation_progress",
        extra={
            "phase": event.phase,
            "percent": event.percent,
            "environment": event.environment,
            "message": event.message,
        },
    )

result = simulate(model, "weather.epw", on_progress=on_progress)
```

### Simple Console Log

```python
from idfkit.simulation import simulate, SimulationProgress

def on_progress(event: SimulationProgress) -> None:
    match event.phase:
        case "warmup":
            print(f"  Warmup iteration {event.warmup_day}")
        case "simulating":
            pct = f"{event.percent:.0f}%" if event.percent else "?"
            print(f"  [{pct}] Simulating {event.environment}")
        case "complete":
            print("  Simulation complete!")

result = simulate(model, "weather.epw", on_progress=on_progress)
```

## WebSocket Forwarding

Forward progress events to a web client for real-time dashboards:

```python
import asyncio
import json
from idfkit.simulation import async_simulate, SimulationProgress

async def run_with_websocket(model, weather, websocket):
    """Run a simulation and forward progress over WebSocket."""
    async def on_progress(event: SimulationProgress) -> None:
        await websocket.send_text(json.dumps({
            "type": "simulation_progress",
            "phase": event.phase,
            "percent": event.percent,
            "message": event.message,
            "environment": event.environment,
        }))

    result = await async_simulate(model, weather, on_progress=on_progress)
    await websocket.send_text(json.dumps({
        "type": "simulation_complete",
        "success": result.success,
        "runtime": result.runtime_seconds,
    }))
    return result
```

### FastAPI Example

```python
from fastapi import FastAPI, WebSocket
from idfkit import load_idf
from idfkit.simulation import async_simulate, SimulationProgress

app = FastAPI()

@app.websocket("/ws/simulate")
async def simulate_ws(websocket: WebSocket):
    await websocket.accept()
    data = await websocket.receive_json()

    model = load_idf(data["idf_path"])

    async def on_progress(event: SimulationProgress) -> None:
        await websocket.send_json({
            "phase": event.phase,
            "percent": event.percent,
            "message": event.message,
        })

    result = await async_simulate(
        model,
        data["weather_path"],
        on_progress=on_progress,
    )

    await websocket.send_json({
        "phase": "done",
        "success": result.success,
        "runtime": result.runtime_seconds,
    })
    await websocket.close()
```

## Batch Progress

In batch mode, `on_progress` fires for every simulation in the batch.
Events include `job_index` and `job_label` to identify which job they
belong to.

### Dual Progress Tracking

Use `on_progress` for intra-simulation progress and `progress` for
job-level completion — they are independent and complementary:

```python
from idfkit.simulation import simulate_batch, SimulationJob, SimulationProgress

jobs = [
    SimulationJob(model=variant, weather="weather.epw", label=f"case-{i}")
    for i, variant in enumerate(variants)
]

def on_sim_progress(event: SimulationProgress) -> None:
    """Fires during each simulation (warmup, simulating, etc.)."""
    if event.percent is not None:
        print(f"  Job {event.job_index} ({event.job_label}): {event.percent:.0f}%")

def on_job_complete(completed, total, label, success):
    """Fires when each job finishes."""
    status = "OK" if success else "FAIL"
    print(f"[{completed}/{total}] {label}: {status}")

batch = simulate_batch(
    jobs,
    on_progress=on_sim_progress,
    progress=on_job_complete,
    max_workers=4,
)
```

### Batch Progress Bar with tqdm

```python
from tqdm import tqdm
from idfkit.simulation import simulate_batch, SimulationJob, SimulationProgress

jobs = [...]

# Job-level progress bar
overall = tqdm(total=len(jobs), desc="Batch", position=0)

# Sim-level progress bar (resets per job)
current = tqdm(total=100, desc="Current", position=1, leave=False)

def on_progress(event: SimulationProgress) -> None:
    if event.percent is not None:
        current.n = event.percent
        current.refresh()
    current.set_postfix_str(event.job_label or "")

def on_job_complete(completed, total, label, success):
    overall.update(1)
    current.n = 0
    current.refresh()

batch = simulate_batch(
    jobs,
    on_progress=on_progress,
    progress=on_job_complete,
    max_workers=4,
)

overall.close()
current.close()
```

### Async Batch with Stream + Progress

Combine `async_simulate_batch_stream` (job-level events) with
`on_progress` (intra-simulation events):

```python
import asyncio
from idfkit.simulation import (
    async_simulate_batch_stream,
    SimulationJob,
    SimulationProgress,
)

async def main():
    jobs = [
        SimulationJob(model=variant, weather="weather.epw", label=f"case-{i}")
        for i, variant in enumerate(variants)
    ]

    def on_sim_progress(event: SimulationProgress) -> None:
        if event.percent is not None:
            print(f"  [{event.job_label}] {event.percent:.0f}%")

    async for event in async_simulate_batch_stream(
        jobs,
        max_concurrent=4,
        on_progress=on_sim_progress,
    ):
        status = "OK" if event.result.success else "FAIL"
        print(f"[{event.completed}/{event.total}] {event.label}: {status}")

asyncio.run(main())
```

## Using ProgressParser Directly

The `ProgressParser` class can be used independently to parse EnergyPlus
stdout output — useful for custom integrations or when processing log files
from previous simulation runs:

```python
from idfkit.simulation import ProgressParser

parser = ProgressParser()

# Parse a log file
with open("energyplus_stdout.log") as f:
    for line in f:
        event = parser.parse_line(line)
        if event is not None:
            print(f"{event.phase}: {event.message}")
```

The parser is stateful (it tracks environment transitions and warmup
counters), so use a fresh instance for each simulation. Non-progress lines
return `None` and never raise exceptions.

## Cloud Execution

When using the `fs` parameter for remote storage, progress callbacks fire
during the local EnergyPlus execution — before results are uploaded.  This
works identically to local execution:

```python
from idfkit.simulation import simulate, S3FileSystem, SimulationProgress

fs = S3FileSystem(bucket="my-bucket", prefix="runs/")

def on_progress(event: SimulationProgress) -> None:
    # This fires during local execution, before upload
    print(f"{event.phase}: {event.percent}")

result = simulate(
    model, "weather.epw",
    output_dir="run-001",
    fs=fs,
    on_progress=on_progress,
)
```

For remote execution scenarios (where EnergyPlus runs on a different machine),
use the async callback to forward events over a transport layer
(WebSocket, SSE, message queue). The `SimulationProgress` dataclass is
JSON-serializable via `dataclasses.asdict()`:

```python
from dataclasses import asdict
import json

def on_progress(event: SimulationProgress) -> None:
    message_queue.publish(json.dumps(asdict(event)))
```

## Behavior Notes

- **No callback, no overhead**: When `on_progress` is not provided, the
  original `subprocess.run()` / `proc.communicate()` code paths are used
  with no performance impact.

- **Callback exceptions**: If your callback raises an exception, the
  simulation is killed and `SimulationError` is raised.

- **Thread safety (batch)**: In `simulate_batch()`, the `on_progress`
  callback may be called from multiple threads concurrently. If your
  callback writes to shared state, ensure it is thread-safe (e.g. use a
  lock or thread-safe data structures).

- **Indeterminate phases**: During warmup and post-processing, `percent`
  is `None`. Your progress indicator should handle this gracefully —
  show a spinner or simply log the phase name.

## API Reference

### Functions

| Function | `on_progress` Support |
|----------|----------------------|
| `simulate()` | Sync callback |
| `async_simulate()` | Sync or async callback |
| `simulate_batch()` | Sync callback (with `job_index`/`job_label`) |
| `async_simulate_batch()` | Sync or async callback (with `job_index`/`job_label`) |
| `async_simulate_batch_stream()` | Sync or async callback (with `job_index`/`job_label`) |

### Classes

| Class | Description |
|-------|-------------|
| `SimulationProgress` | Frozen dataclass for progress events |
| `ProgressParser` | Stateful EnergyPlus stdout line parser |

## See Also

- [Running Simulations](running.md) — Full `simulate()` parameter reference
- [Async Simulation](async.md) — Non-blocking execution guide
- [Batch Processing](batch.md) — Parallel execution guide
