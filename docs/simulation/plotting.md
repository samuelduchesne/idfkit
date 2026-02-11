# Plotting

The simulation module provides pluggable plotting backends for visualizing
results with matplotlib or plotly.

## Quick Start

```python
--8<-- "docs/snippets/simulation/plotting/quick_start.py"
```

## Installation

Install a plotting backend:

```bash
# Matplotlib (recommended for static plots)
pip install idfkit[plot]

# Plotly (for interactive plots)
pip install idfkit[plotly]

# Both
pip install idfkit[plot,plotly]
```

## Built-in Visualizations

### Temperature Profile

```python
--8<-- "docs/snippets/simulation/plotting/temperature_profile.py"
```

### Energy Balance

```python
--8<-- "docs/snippets/simulation/plotting/energy_balance.py"
```

### Comfort Hours

```python
--8<-- "docs/snippets/simulation/plotting/comfort_hours.py"
```

## Time Series Plotting

`TimeSeriesResult` has a built-in `plot()` method:

```python
--8<-- "docs/snippets/simulation/plotting/time_series_plotting.py"
```

## Backend Selection

### Auto-Detection

By default, the first available backend is used:

```python
--8<-- "docs/snippets/simulation/plotting/auto_detection.py"
```

Priority: matplotlib → plotly

### Explicit Backend

```python
--8<-- "docs/snippets/simulation/plotting/explicit_backend.py"
```

## PlotBackend Protocol

Create custom backends by implementing the `PlotBackend` protocol:

```python
--8<-- "docs/snippets/simulation/plotting/plotbackend_protocol.py"
```

## Matplotlib Backend

### Basic Usage

```python
--8<-- "docs/snippets/simulation/plotting/basic_usage.py"
```

### Customization

```python
--8<-- "docs/snippets/simulation/plotting/customization.py"
```

## Plotly Backend

### Basic Usage

```python
--8<-- "docs/snippets/simulation/plotting/basic_usage_2.py"
```

### Customization

```python
--8<-- "docs/snippets/simulation/plotting/customization_2.py"
```

## DataFrame Integration

Convert to pandas and use native plotting:

```python
--8<-- "docs/snippets/simulation/plotting/dataframe_integration.py"
```

## Multiple Time Series

### Same Variable, Multiple Keys

```python
--8<-- "docs/snippets/simulation/plotting/same_variable_multiple_keys.py"
```

### Different Variables

```python
--8<-- "docs/snippets/simulation/plotting/different_variables.py"
```

## Saving Figures

### Matplotlib

```python
--8<-- "docs/snippets/simulation/plotting/matplotlib.py"
```

### Plotly

```python
--8<-- "docs/snippets/simulation/plotting/plotly.py"
```

## See Also

- [SQL Output Queries](sql-queries.md) — Getting time series data
- [Parsing Results](results.md) — Working with SimulationResult
- [Examples: Parametric Study](../examples/parametric-study.ipynb) — Visualization examples
