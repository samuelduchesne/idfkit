# Simulation API Overview

The simulation module provides EnergyPlus execution and result parsing.

## Quick Reference

| Function/Class | Description |
|---------------|-------------|
| [`simulate()`](runner.md) | Run a single simulation |
| [`simulate_batch()`](batch.md) | Run multiple simulations in parallel |
| [`async_simulate()`](async.md) | Non-blocking single simulation |
| [`async_simulate_batch()`](async.md) | Non-blocking parallel simulations |
| [`async_simulate_batch_stream()`](async.md) | Streaming progress via async generator |
| [`SimulationEvent`](async.md) | Progress event from streaming batch |
| [`find_energyplus()`](runner.md) | Discover EnergyPlus installation |
| [`expand_objects()`](expand.md) | Expand `HVACTemplate:*` objects |
| [`run_slab_preprocessor()`](expand.md) | Run the Slab ground heat-transfer preprocessor |
| [`run_basement_preprocessor()`](expand.md) | Run the Basement ground heat-transfer preprocessor |
| [`run_preprocessing()`](expand.md) | Run all needed preprocessors (combined pipeline) |
| [`needs_ground_heat_preprocessing()`](expand.md) | Check if model needs GHT preprocessing |
| [`SimulationResult`](results.md) | Simulation result container |
| [`SimulationJob`](batch.md) | Job specification for batch runs |
| [`BatchResult`](batch.md) | Aggregated batch results |
| [`SQLResult`](sql.md) | SQL database query interface |
| [`SimulationCache`](cache.md) | Content-addressed result cache |
| [`FileSystem`](fs.md) | Pluggable storage protocol |
| [`S3FileSystem`](fs.md) | Amazon S3 storage backend |

## Module Contents

::: idfkit.simulation
    options:
      show_root_heading: false
      show_source: false
      members_order: source
      filters:
        - "!^_"
