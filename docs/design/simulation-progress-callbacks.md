# Design: Simulation Progress Callbacks

## Problem Statement

Users running EnergyPlus simulations via idfkit have no visibility into what
is happening *during* a single simulation run. The existing APIs are
fire-and-forget: `simulate()` blocks and returns a `SimulationResult`;
`async_simulate()` awaits and returns the same. Batch-level progress exists
(`simulate_batch` accepts a `progress` callback, `async_simulate_batch_stream`
yields `SimulationEvent`s), but these only fire **between** jobs, not within
them.

For long-running annual simulations (minutes to hours), users need
intra-simulation progress for:

- **Jupyter/console**: tqdm or rich progress bars
- **Web dashboards**: live updates via WebSocket or SSE
- **Cloud pipelines**: structured log streams for monitoring
- **Batch orchestration**: estimated time remaining across a sweep

---

## Progress Information Available from EnergyPlus

### Source 1: Stdout Line Parsing (no runtime API dependency)

EnergyPlus writes structured progress lines to stdout during execution:

```
EnergyPlus, Version 24.1.0-...
Initializing New Environment Parameters
Warming up {1}
Warming up {2}
...
Warming up {N}
Starting Simulation at 01/01/2017 for CHICAGO AnnualRun
Updating Coverage for Reporting Period at 01/01/2017 00:15:00
Updating Shadowing Calculations
Continuing Simulation at 02/01/2017 for CHICAGO AnnualRun
...
Writing tabular output file results using comma format.
Writing final SQL reports
EnergyPlus Completed Successfully.
```

**Identifiable phases:**

| Pattern | Phase | Percent Estimable? |
|---------|-------|--------------------|
| `Initializing New Environment` | init | No (instant) |
| `Warming up {N}` | warmup | Only count (no total) |
| `Starting Simulation at MM/DD` | simulating | Yes — date / period |
| `Continuing Simulation at MM/DD` | simulating | Yes — date / period |
| `Writing tabular output` | postprocessing | No (instant) |
| `Writing final SQL reports` | postprocessing | No (instant) |
| `EnergyPlus Completed` | done | 100% |

**Percentage estimation during simulation phase:** If the simulation period is
known (annual = 365 days, or extractable from the `Starting Simulation at
MM/DD/YYYY ... to MM/DD/YYYY` line), the current date from `Continuing
Simulation at MM/DD` can give a reasonable percentage. For design-day runs
the simulation phase is short and progress bars matter less.

**Multiple environments:** A single EnergyPlus run may simulate multiple
environments (e.g. sizing periods + annual). Each restarts the warmup →
simulate cycle. The parser needs to track environment transitions to provide
meaningful cumulative progress.

### Source 2: EnergyPlus Python Runtime API (`pyenergyplus.api`)

EnergyPlus 9.3+ ships with Python bindings that provide in-process execution
and registered callbacks:

```python
from pyenergyplus.api import EnergyPlusAPI

api = EnergyPlusAPI()
state = api.state_manager.new_state()

# Integer 0-100 progress — exactly what we need
api.runtime.callback_progress(state, lambda progress: print(f"{progress}%"))

# Text messages (same as stdout lines)
api.runtime.callback_message(state, lambda msg: print(msg))

# Fine-grained simulation hooks
api.runtime.callback_begin_new_environment_after_warm_up(state, func)
api.runtime.callback_begin_zone_timestep_before_init_heat_balance(state, func)
api.runtime.callback_end_zone_timestep_after_zone_reporting(state, func)

# Run in-process (NOT as subprocess)
api.runtime.run_energyplus(state, ['-w', 'weather.epw', '-d', 'out/', 'in.idf'])
```

**Key difference:** The runtime API runs EnergyPlus **in-process** via a
shared library (`libenergyplusapi.so` / `EnergyPlusAPI.dll`), not as a
subprocess. This is a fundamentally different execution model.

### Source 3: File Watching

Monitor the `.err` file or `.eso` file for growth during simulation. The
`.err` file contains timestamped progress messages similar to stdout.

**Verdict:** Fragile, introduces polling/inotify complexity, and provides no
information that stdout doesn't already give. Not recommended.

---

## Design Options

### Option A: Stdout Line Streaming (Recommended Primary Approach)

Replace `subprocess.run(capture_output=True)` / `proc.communicate()` with
line-by-line stdout reading and parse progress events in real time.

#### Sync implementation sketch

```python
# runner.py — core change
proc = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    cwd=str(run_dir),
)

stdout_lines: list[str] = []
parser = ProgressParser()  # stateful — tracks environment transitions

for line in proc.stdout:             # blocks per-line, not per-run
    stdout_lines.append(line)
    event = parser.parse_line(line)
    if event is not None and on_progress is not None:
        on_progress(event)

stderr = proc.stderr.read()
proc.wait()
```

#### Async implementation sketch

```python
# async_runner.py — core change
proc = await asyncio.create_subprocess_exec(
    *cmd,
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE,
    cwd=str(run_dir),
)

stdout_lines: list[str] = []
parser = ProgressParser()

async for raw_line in proc.stdout:  # non-blocking per-line
    line = raw_line.decode("utf-8", errors="replace")
    stdout_lines.append(line)
    event = parser.parse_line(line)
    if event is not None and on_progress is not None:
        if asyncio.iscoroutinefunction(on_progress):
            await on_progress(event)
        else:
            on_progress(event)

stderr_bytes = await proc.stderr.read()
await proc.wait()
```

#### Pros

- **Zero new dependencies** — works with any EnergyPlus version
- **Subprocess model preserved** — no architectural change, batch parallelism
  unaffected (threads/semaphores still work)
- **Cloud-compatible** — callback fires during local execution; consumer
  can forward to any sink (WebSocket, log stream, database)
- **Testable** — `ProgressParser` is a pure function over strings, easy to
  unit-test with captured stdout samples

#### Cons

- **Estimated percentage** — no native 0-100; must derive from date parsing
  or fall back to indeterminate progress
- **Parsing fragility** — stdout format could change between EnergyPlus
  versions (mitigated by defensive parsing that degrades to raw messages)
- **Stderr buffering** — with Popen, stderr is read after stdout completes;
  for very large stderr output this could theoretically block. Can be
  mitigated with a stderr reader thread (sync) or concurrent read (async).

### Option B: EnergyPlus Python Runtime API

Replace subprocess execution with in-process execution via `pyenergyplus.api`.

#### Pros

- **Native 0-100% progress** via `callback_progress`
- **Fine-grained hooks** — per-timestep callbacks enable detailed monitoring
- **Rich data access** — can read actuator/variable values mid-simulation

#### Cons

- **Hard dependency on `pyenergyplus`** — not always available, especially in
  Docker/CI/cloud images that only ship the CLI binary
- **In-process execution** — EnergyPlus runs in the Python process, not as a
  subprocess. Crashes in EnergyPlus take down the Python process.
- **No parallel batch** — the EnergyPlus runtime is single-threaded and uses
  global state. Running multiple simulations requires multiple processes
  anyway, negating the benefit over subprocess.
- **Thread safety** — `callback_progress` is called from the EnergyPlus
  thread; the callback must be thread-safe
- **API surface change** — fundamentally different execution model; would
  need a separate code path alongside the existing subprocess runner
- **Preprocessing complications** — ExpandObjects, Slab, Basement are
  separate executables that still need subprocess invocation

#### Verdict

The runtime API is best suited as an **optional enhancement** for users who
have it available and want per-timestep granularity, not as the primary
progress mechanism. It should not be a hard requirement.

### Option C: Hybrid (Recommended)

Use stdout line streaming as the primary mechanism (Option A). Optionally
detect the EnergyPlus Python API and use `callback_progress` for accurate
percentage when available. This can be a future enhancement layered on top of
Option A.

---

## Proposed API

### Progress Event Model

```python
@dataclass(frozen=True, slots=True)
class SimulationProgress:
    """Progress event emitted during a single EnergyPlus simulation."""

    phase: Literal["preprocessing", "warmup", "simulating", "postprocessing", "complete"]
    message: str                      # Raw EnergyPlus stdout line (stripped)
    percent: float | None = None      # 0.0–100.0, None if indeterminate
    environment: str | None = None    # Current environment name
    warmup_day: int | None = None     # Current warmup iteration (1-based)
    sim_day: int | None = None        # Current simulation day (1-based)
    sim_total_days: int | None = None # Total simulation days (if known)
```

### Callback Protocol

```python
# Type alias — kept simple, no Protocol class needed
ProgressCallback = Callable[[SimulationProgress], None]

# For async, accept both sync and async callables:
# - Sync callback: called directly (useful for thread-safe tqdm.update)
# - Async callback: awaited (useful for WebSocket forwarding)
```

### Single Simulation API Changes

```python
def simulate(
    model: IDFDocument,
    weather: str | Path,
    *,
    on_progress: ProgressCallback | None = None,  # NEW
    # ... all existing parameters unchanged ...
) -> SimulationResult:

async def async_simulate(
    model: IDFDocument,
    weather: str | Path,
    *,
    on_progress: ProgressCallback | Callable[[SimulationProgress], Awaitable[None]] | None = None,  # NEW
    # ... all existing parameters unchanged ...
) -> SimulationResult:
```

### Batch API Changes

The existing `progress` callback on `simulate_batch` tracks **job-level**
progress (which jobs have completed). `on_progress` tracks **simulation-level**
progress (what's happening inside a single job). Both are useful and
orthogonal.

```python
def simulate_batch(
    jobs: Sequence[SimulationJob],
    *,
    on_progress: ProgressCallback | None = None,  # NEW — per-simulation progress
    progress: Callable[..., None] | None = None,   # existing — per-job completion
    # ...
) -> BatchResult:
```

For batch, the callback should include the job identity. Two options:

**Option 1 — Extend SimulationProgress with job context:**
```python
@dataclass(frozen=True, slots=True)
class SimulationProgress:
    # ... existing fields ...
    job_index: int | None = None   # None for single simulate(), set for batch
    job_label: str | None = None
```

**Option 2 — Wrap in a separate batch event (more complex, probably
unnecessary):**
Skip this — Option 1 is simpler and sufficient.

### Streaming Batch

`async_simulate_batch_stream` already yields `SimulationEvent` on job
completion. Intra-simulation progress is harder to expose through a single
stream because it mixes two levels of events. Two approaches:

**Approach A — Dual stream (new function):**
```python
@dataclass(frozen=True, slots=True)
class BatchProgressEvent:
    """Union of job-completion and intra-simulation progress events."""
    kind: Literal["progress", "completed"]
    job_index: int
    job_label: str
    progress: SimulationProgress | None = None  # set when kind="progress"
    result: SimulationResult | None = None       # set when kind="completed"
    completed_count: int = 0
    total: int = 0
```

**Approach B — Callback on the stream (simpler):**
Keep `async_simulate_batch_stream` as-is for job-level events. Pass
`on_progress` through to the inner `async_simulate` calls for
intra-simulation progress. Users who need both can combine:

```python
async for event in async_simulate_batch_stream(
    jobs,
    on_progress=lambda p: update_individual_bar(p),  # intra-sim
):
    update_overall_bar(event)  # job-level
```

**Recommendation:** Approach B — it preserves the existing stream contract
and avoids a heterogeneous event union.

---

## Stdout Parser Design

### `ProgressParser`

A stateful parser that tracks environment transitions and estimates progress:

```python
class ProgressParser:
    """Parse EnergyPlus stdout lines into SimulationProgress events.

    Maintains state across lines to track the current environment,
    warmup iteration, and simulation day for percentage estimation.
    """

    _RE_WARMUP = re.compile(r"Warming up \{(\d+)\}")
    _RE_START_SIM = re.compile(
        r"Starting Simulation at (\d{2}/\d{2}(?:/\d{4})?) for (.+)"
    )
    _RE_CONTINUE_SIM = re.compile(
        r"Continuing Simulation at (\d{2}/\d{2}(?:/\d{4})?) for (.+)"
    )
    _RE_COMPLETED = re.compile(r"EnergyPlus Completed Successfully")

    def parse_line(self, line: str) -> SimulationProgress | None:
        """Parse a single stdout line. Returns None for non-progress lines."""
        ...
```

The parser should be:
- **Defensive** — unrecognized lines return `None`, never raise
- **Version-tolerant** — regex patterns should be loose enough to handle
  minor format changes
- **Stateful per-simulation** — reset between simulations in batch mode
- **Pure aside from internal state** — no I/O, easy to unit-test

### Percentage Estimation Strategy

For an annual simulation (365 days), once we see `Starting Simulation at
01/01`, each `Continuing Simulation at MM/DD` can be converted to a
day-of-year and divided by 365. For non-annual runs, we can extract the
period from the `Starting Simulation ... from MM/DD to MM/DD` line.

When the period is unknown, `percent` is `None` (indeterminate) and consumers
fall back to a spinner or indeterminate progress bar.

---

## Integration Examples

### tqdm (Console)

```python
from tqdm import tqdm

bar = tqdm(total=100, desc="Simulating", unit="%")

def on_progress(p: SimulationProgress) -> None:
    if p.percent is not None:
        bar.update(p.percent - bar.n)
    bar.set_postfix_str(p.phase)

result = simulate(model, weather, on_progress=on_progress)
bar.close()
```

### rich (Console)

```python
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

with Progress(
    SpinnerColumn(),
    TextColumn("[bold]{task.description}"),
    BarColumn(),
    TextColumn("{task.percentage:>3.0f}%"),
) as progress:
    task = progress.add_task("Simulating", total=100)

    def on_progress(p: SimulationProgress) -> None:
        if p.percent is not None:
            progress.update(task, completed=p.percent)
        progress.update(task, description=p.phase)

    result = simulate(model, weather, on_progress=on_progress)
```

### Jupyter (ipywidgets)

```python
import ipywidgets as widgets
from IPython.display import display

bar = widgets.FloatProgress(min=0, max=100, description="Simulating:")
label = widgets.Label()
display(widgets.HBox([bar, label]))

def on_progress(p: SimulationProgress) -> None:
    if p.percent is not None:
        bar.value = p.percent
    label.value = p.message

result = simulate(model, weather, on_progress=on_progress)
```

### WebSocket Forwarding (Async)

```python
async def on_progress(p: SimulationProgress) -> None:
    await websocket.send_json({
        "phase": p.phase,
        "percent": p.percent,
        "message": p.message,
        "environment": p.environment,
    })

result = await async_simulate(model, weather, on_progress=on_progress)
```

### Cloud Log Stream

```python
import logging

logger = logging.getLogger("simulation")

def on_progress(p: SimulationProgress) -> None:
    logger.info(
        "simulation_progress",
        extra={"phase": p.phase, "percent": p.percent, "env": p.environment},
    )

result = simulate(model, weather, on_progress=on_progress)
```

### Batch with Dual Progress

```python
from tqdm import tqdm

jobs = [SimulationJob(model=m, weather=w, label=f"run-{i}") for i, (m, w) in enumerate(runs)]

overall = tqdm(total=len(jobs), desc="Batch", position=0)
current = tqdm(total=100, desc="Current", position=1, leave=False)

def on_progress(p: SimulationProgress) -> None:
    if p.percent is not None:
        current.update(p.percent - current.n)
    current.set_postfix_str(p.job_label or "")

def on_job_complete(*, completed: int, total: int, label: str, success: bool) -> None:
    overall.update(1)
    current.reset()

batch = simulate_batch(
    jobs,
    on_progress=on_progress,
    progress=on_job_complete,
)
```

---

## Cloud Execution Considerations

### Current Model: Local Execution + Remote Storage

idfkit currently runs EnergyPlus locally and optionally uploads results to S3
via the `fs` parameter. In this model, progress callbacks work identically to
local execution — the callback fires during the local subprocess run, and the
consumer can forward events to any sink.

### Future Model: Remote Execution

If idfkit were to support dispatching simulations to remote workers (Lambda,
Fargate, Kubernetes jobs, etc.), progress reporting would need a transport layer:

| Transport | Latency | Complexity | Best For |
|-----------|---------|------------|----------|
| **WebSocket** | Low (~ms) | Medium | Web dashboards, real-time UIs |
| **SSE (Server-Sent Events)** | Low (~ms) | Low | One-way progress to browser |
| **Polling (HTTP)** | Medium (~1s) | Low | Simple integrations |
| **Cloud log tailing** (CloudWatch, etc.) | Medium (~1-5s) | Low | Cloud-native pipelines |
| **Message queue** (SQS, Redis pub/sub) | Low-Medium | Medium | Distributed systems |

**Recommendation for remote execution:** The `on_progress` callback model
still works — the remote worker captures stdout, parses progress, and
publishes events to a message broker or log stream. The client-side library
provides a matching consumer:

```python
# Hypothetical remote execution
async for event in remote_simulate_stream(model, weather, endpoint="https://..."):
    print(f"{event.phase}: {event.percent}%")
```

This is out of scope for the current design but the callback + dataclass
model is forward-compatible: `SimulationProgress` can be serialized to JSON
and deserialized on the client side.

---

## Implementation Plan

### Phase 1: Core (Recommended Scope)

1. **Add `SimulationProgress` dataclass** to `idfkit.simulation.progress`
2. **Implement `ProgressParser`** with regex-based stdout line parsing
3. **Modify `simulate()`** — switch from `subprocess.run` to `Popen` with
   line-by-line stdout reading; add `on_progress` parameter
4. **Modify `async_simulate()`** — switch from `proc.communicate()` to async
   line-by-line reading; add `on_progress` parameter
5. **Thread `on_progress` through batch APIs** — `simulate_batch`,
   `async_simulate_batch`, `async_simulate_batch_stream`
6. **Add `SimulationJob.on_progress`** field for per-job callbacks in batch
7. **Unit tests** for `ProgressParser` with captured EnergyPlus stdout samples
8. **Integration tests** verifying callbacks fire during simulation

### Phase 2: Enhancements (Future)

- **Runtime API backend** — detect `pyenergyplus.api` availability and use
  `callback_progress` for native 0-100% when possible
- **Period extraction** — parse simulation period from `RunPeriod` objects in
  the model to improve percentage estimation
- **Preprocessing progress** — emit events during ExpandObjects/Slab/Basement
  preprocessing steps
- **Structured logging integration** — optional `logging.Logger` parameter
  for automatic structured log emission

---

## Key Design Decisions

### Why `on_progress` callback, not an event emitter or observable?

- **Simplicity** — a callback is the simplest possible interface; users
  already understand `progress=` on the batch API
- **Sync/async duality** — a callback works in both contexts (sync callable
  vs awaitable)
- **No new abstractions** — no event emitter, observable, or pub/sub system
  to learn
- **Composable** — users wrap the callback to connect to any sink (tqdm,
  rich, WebSocket, logging)

### Why not return an iterator from `simulate()`?

Changing `simulate()` to return an iterator of progress events would break
the existing API contract (returns `SimulationResult`). It would also make
the common case (just get the result) more complex. The callback is additive
— existing code continues to work without modification.

### Why `Popen` instead of keeping `subprocess.run`?

`subprocess.run` with `capture_output=True` buffers all stdout until the
process exits. There is no way to read lines incrementally. `Popen` with
`PIPE` and line-by-line iteration is the standard approach for real-time
subprocess output processing.

### Why not use the `--output-json` flag?

EnergyPlus does not have a `--output-json` flag for structured progress
output. The stdout format is the only real-time progress source when using
subprocess execution.

### Why `percent: float | None` instead of always providing a number?

During warmup and postprocessing, the total duration is unknown. Forcing a
percentage would require fabricating numbers (e.g., "warmup is 10%"), which
misleads users. `None` signals "indeterminate" and lets consumers show a
spinner instead of a bar.

### Why accept both sync and async callables in `async_simulate`?

Many progress consumers (tqdm, rich) are synchronous. Requiring an async
callback would force users to write `async def` wrappers for simple updates.
Accepting both is more ergonomic. The implementation checks with
`asyncio.iscoroutinefunction()` and awaits when needed.
