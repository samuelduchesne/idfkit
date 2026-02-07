"""Async batch simulation with semaphore-based concurrency control.

Non-blocking counterpart to :func:`~idfkit.simulation.batch.simulate_batch`
that uses :mod:`asyncio` for concurrency instead of
:class:`~concurrent.futures.ThreadPoolExecutor`.

Two entry points are provided:

* :func:`async_simulate_batch` — runs all jobs and returns an aggregated
  :class:`~idfkit.simulation.batch.BatchResult`, mirroring the sync API.
* :func:`async_simulate_batch_stream` — an async generator that yields
  :class:`SimulationEvent` objects as each simulation completes, enabling
  real-time progress monitoring without callbacks.

Example::

    import asyncio
    from idfkit.simulation import async_simulate_batch, SimulationJob

    async def main():
        jobs = [SimulationJob(model=m, weather="weather.epw", label=f"run-{i}") for i, m in enumerate(models)]
        batch = await async_simulate_batch(jobs, max_concurrent=4)
        print(f"{len(batch.succeeded)}/{len(batch)} succeeded")

    asyncio.run(main())

Streaming example::

    from idfkit.simulation import async_simulate_batch_stream

    async def main():
        jobs = [...]
        async for event in async_simulate_batch_stream(jobs, max_concurrent=4):
            status = "OK" if event.result.success else "FAIL"
            print(f"[{event.completed}/{event.total}] {event.label}: {status}")
"""

from __future__ import annotations

import asyncio
import os
import time
from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from ..exceptions import SimulationError
from .async_runner import async_simulate
from .batch import BatchResult, SimulationJob
from .result import SimulationResult

if TYPE_CHECKING:
    from .cache import SimulationCache
    from .config import EnergyPlusConfig
    from .fs import FileSystem


@dataclass(frozen=True, slots=True)
class SimulationEvent:
    """Progress event emitted by :func:`async_simulate_batch_stream`.

    Each event represents a single simulation that has finished (successfully
    or not).  Events are yielded in *completion order*, not submission order.

    Attributes:
        index: Zero-based position of this job in the original *jobs* sequence.
        label: Human-readable label from the :class:`SimulationJob`.
        result: The simulation result.
        completed: Number of jobs completed so far (including this one).
        total: Total number of jobs in the batch.
    """

    index: int
    label: str
    result: SimulationResult
    completed: int
    total: int


async def async_simulate_batch(
    jobs: Sequence[SimulationJob],
    *,
    energyplus: EnergyPlusConfig | None = None,
    max_concurrent: int | None = None,
    cache: SimulationCache | None = None,
    fs: FileSystem | None = None,
) -> BatchResult:
    """Run multiple EnergyPlus simulations concurrently using asyncio.

    This is the async counterpart to
    :func:`~idfkit.simulation.batch.simulate_batch`.  Concurrency is
    controlled with an :class:`asyncio.Semaphore` instead of a thread pool.

    Individual job failures are captured as failed
    :class:`~idfkit.simulation.result.SimulationResult` entries — the batch
    never raises due to a single job failing.

    Args:
        jobs: Sequence of simulation jobs to execute.
        energyplus: Shared EnergyPlus configuration (auto-discovered if
            ``None``).
        max_concurrent: Maximum number of concurrent simulations.  Defaults
            to ``min(len(jobs), os.cpu_count() or 1)``.
        cache: Optional simulation cache for content-hash lookups.
        fs: Optional file system backend passed through to each
            :func:`~idfkit.simulation.async_runner.async_simulate` call.

    Returns:
        A :class:`~idfkit.simulation.batch.BatchResult` with results in the
        same order as *jobs*.

    Raises:
        ValueError: If *jobs* is empty.
    """
    if not jobs:
        msg = "jobs must not be empty"
        raise ValueError(msg)

    if max_concurrent is None:
        max_concurrent = min(len(jobs), os.cpu_count() or 1)

    semaphore = asyncio.Semaphore(max_concurrent)
    results: list[SimulationResult | None] = [None] * len(jobs)
    start = time.monotonic()

    async def _run_one(idx: int, job: SimulationJob) -> None:
        async with semaphore:
            results[idx] = await _async_run_job(job, energyplus, cache, fs)

    tasks = [asyncio.create_task(_run_one(i, job)) for i, job in enumerate(jobs)]
    await asyncio.gather(*tasks)

    elapsed = time.monotonic() - start

    final: list[SimulationResult] = []
    for r in results:
        assert r is not None  # noqa: S101
        final.append(r)

    return BatchResult(results=tuple(final), total_runtime_seconds=elapsed)


async def async_simulate_batch_stream(
    jobs: Sequence[SimulationJob],
    *,
    energyplus: EnergyPlusConfig | None = None,
    max_concurrent: int | None = None,
    cache: SimulationCache | None = None,
    fs: FileSystem | None = None,
) -> AsyncIterator[SimulationEvent]:
    """Run simulations concurrently, yielding events as each one completes.

    This is an async generator variant of :func:`async_simulate_batch` that
    yields :class:`SimulationEvent` objects in *completion order*.  This
    enables real-time progress reporting without needing a callback:

    .. code-block:: python

        async for event in async_simulate_batch_stream(jobs, max_concurrent=4):
            print(f"[{event.completed}/{event.total}] {event.label}")

    Args:
        jobs: Sequence of simulation jobs to execute.
        energyplus: Shared EnergyPlus configuration (auto-discovered if
            ``None``).
        max_concurrent: Maximum number of concurrent simulations.  Defaults
            to ``min(len(jobs), os.cpu_count() or 1)``.
        cache: Optional simulation cache for content-hash lookups.
        fs: Optional file system backend.

    Yields:
        :class:`SimulationEvent` for each completed simulation, in the order
        they finish.

    Raises:
        ValueError: If *jobs* is empty.
    """
    if not jobs:
        msg = "jobs must not be empty"
        raise ValueError(msg)

    if max_concurrent is None:
        max_concurrent = min(len(jobs), os.cpu_count() or 1)

    semaphore = asyncio.Semaphore(max_concurrent)
    total = len(jobs)
    queue: asyncio.Queue[SimulationEvent] = asyncio.Queue()
    completed_count = 0

    async def _run_one(idx: int, job: SimulationJob) -> None:
        nonlocal completed_count
        async with semaphore:
            result = await _async_run_job(job, energyplus, cache, fs)
        completed_count += 1
        await queue.put(
            SimulationEvent(
                index=idx,
                label=job.label,
                result=result,
                completed=completed_count,
                total=total,
            )
        )

    tasks = [asyncio.create_task(_run_one(i, job)) for i, job in enumerate(jobs)]

    try:
        for _ in range(total):
            event = await queue.get()
            yield event
    finally:
        # If the consumer breaks out early, cancel remaining tasks.
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


async def _async_run_job(
    job: SimulationJob,
    energyplus: EnergyPlusConfig | None,
    cache: SimulationCache | None,
    fs: FileSystem | None,
) -> SimulationResult:
    """Execute a single simulation job, catching SimulationError."""
    try:
        return await async_simulate(
            model=job.model,  # type: ignore[arg-type]
            weather=job.weather,
            output_dir=job.output_dir,
            energyplus=energyplus,
            expand_objects=job.expand_objects,
            annual=job.annual,
            design_day=job.design_day,
            output_prefix=job.output_prefix,
            output_suffix=job.output_suffix,
            readvars=job.readvars,
            timeout=job.timeout,
            extra_args=list(job.extra_args) if job.extra_args else None,
            cache=cache,
            fs=fs,
        )
    except SimulationError as exc:
        failed_run_dir = Path(job.output_dir) if job.output_dir is not None else Path("/dev/null")
        return SimulationResult(
            run_dir=failed_run_dir,
            success=False,
            exit_code=exc.exit_code,
            stdout="",
            stderr=exc.stderr or "",
            runtime_seconds=0.0,
            output_prefix=job.output_prefix,
        )
