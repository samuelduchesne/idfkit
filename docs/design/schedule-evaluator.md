# Schedule Evaluator Module Design

## Overview

A lightweight module to evaluate EnergyPlus schedules without running a simulation.
Returns the schedule value at any given datetime or produces hourly time series.

## Goals

1. **Minimal dependencies** - Core functionality requires only stdlib; pandas/matplotlib optional
2. **Works with existing idfkit** - Operates on `IDFObject` instances from `IDFDocument`
3. **Correct EnergyPlus semantics** - Matches E+ interpretation of schedule syntax
4. **Composable API** - Low-level `evaluate()` + high-level `to_series()`

## Supported Schedule Types

| Type | Priority | Complexity |
|------|----------|------------|
| `Schedule:Constant` | P0 | Trivial |
| `Schedule:Day:Hourly` | P0 | Simple - 24 values |
| `Schedule:Day:Interval` | P0 | Medium - time/value pairs |
| `Schedule:Day:List` | P1 | Medium - values at fixed intervals |
| `Schedule:Week:Daily` | P0 | Simple - 7 day schedule refs |
| `Schedule:Week:Compact` | P1 | Medium - day type rules |
| `Schedule:Year` | P0 | Medium - date ranges → week refs |
| `Schedule:Compact` | P0 | Complex - nested DSL |
| `Schedule:File` | P2 | External CSV parsing |

## Module Structure

```
src/idfkit/schedules/
├── __init__.py          # Public API exports
├── evaluate.py          # Core evaluation logic + dispatch
├── types.py             # DayType, Interpolation enums, SpecialDay dataclass
├── compact.py           # Schedule:Compact parser
├── day.py               # Day schedule handlers (Hourly, Interval, List)
├── week.py              # Week schedule handlers (Daily, Compact)
├── year.py              # Year schedule + date matching
├── file.py              # Schedule:File CSV reader with FileSystem support
├── holidays.py          # RunPeriodControl:SpecialDays parser
└── series.py            # pandas integration (optional)
```

## Public API

### Core Function

```python
--8<-- "docs/snippets/design/schedule-evaluator/core_function.py"
```

### Batch Evaluation

```python
--8<-- "docs/snippets/design/schedule-evaluator/batch_evaluation.py"
```

### Pandas Integration (optional)

```python
--8<-- "docs/snippets/design/schedule-evaluator/pandas_integration_optional.py"
```

### Convenience on IDFDocument

```python
--8<-- "docs/snippets/design/schedule-evaluator/convenience_on_idfdocument.py"
```

## Schedule:Compact Parser

The most complex part. Schedule:Compact uses a mini-DSL:

```
Schedule:Compact,
  Office Occupancy,        ! Name
  Fraction,                ! Schedule Type Limits
  Through: 12/31,          ! Date range (implicit start 1/1)
  For: Weekdays,           ! Day types
  Until: 08:00, 0.0,       ! Time, Value pairs
  Until: 18:00, 1.0,
  Until: 24:00, 0.0,
  For: Weekends Holidays,
  Until: 24:00, 0.0;
```

### Parsing Strategy

```python
--8<-- "docs/snippets/design/schedule-evaluator/parsing_strategy.py"
```

### Day Type Mapping

EnergyPlus day types to Python weekday:

| E+ Day Type | Python weekday() |
|-------------|------------------|
| Sunday | 6 |
| Monday | 0 |
| Tuesday | 1 |
| Wednesday | 2 |
| Thursday | 3 |
| Friday | 4 |
| Saturday | 5 |
| Weekdays | 0-4 |
| Weekends | 5-6 |
| AllDays | 0-6 |
| Holidays | (requires holiday list) |
| SummerDesignDay | (special) |
| WinterDesignDay | (special) |
| AllOtherDays | (fallback) |

## Hierarchical Schedule Resolution

`Schedule:Year` references `Schedule:Week:*` which references `Schedule:Day:*`:

```python
--8<-- "docs/snippets/design/schedule-evaluator/hierarchical_schedule_resolution.py"
```

## Schedule:Day Evaluation

### Schedule:Day:Hourly

24 values, one per hour:

```python
--8<-- "docs/snippets/design/schedule-evaluator/scheduledayhourly.py"
```

### Schedule:Day:Interval

Time/value pairs where value applies UNTIL that time:

```python
--8<-- "docs/snippets/design/schedule-evaluator/scheduledayinterval.py"
```

## Error Handling

```python
--8<-- "docs/snippets/design/schedule-evaluator/error_handling.py"
```

## Testing Strategy

1. **Unit tests per schedule type** - Test each parser/evaluator in isolation
2. **Known-value tests** - Compare against EnergyPlus ESO output for same schedule
3. **Round-trip tests** - `values()` output matches E+ hourly report
4. **Edge cases** - Leap years, DST (E+ doesn't use DST), midnight boundaries

### Example Test

```python
--8<-- "docs/snippets/design/schedule-evaluator/example_test.py"
```

## Dependencies

### Required
- None (stdlib only for core)

### Internal (from idfkit)
- `idfkit.simulation.fs.FileSystem` - For Schedule:File CSV reading
- `idfkit.simulation.fs.LocalFileSystem` - Default filesystem

### Optional
- `pandas` - for `to_series()` and DataFrame integration

```toml
[project.optional-dependencies]
# No new deps needed - reuse existing
dataframes = ["pandas>=2.0"]  # Already exists
```

### FileSystem Integration

The `FileSystem` protocol enables Schedule:File to work with remote storage:

```python
--8<-- "docs/snippets/design/schedule-evaluator/filesystem_integration.py"
```

## Implementation Order

1. **Phase 1: Foundation** (~120 LOC)
   - `types.py`: Enums (`DayType`, `Interpolation`), `SpecialDay` dataclass
   - `holidays.py`: Parse `RunPeriodControl:SpecialDays`
   - `day.py`: `Schedule:Constant`, `Schedule:Day:Hourly`, `Schedule:Day:Interval`

2. **Phase 2: Hierarchical schedules** (~150 LOC)
   - `week.py`: `Schedule:Week:Daily`, `Schedule:Week:Compact`
   - `year.py`: `Schedule:Year`, date range matching
   - Reference resolution across schedule types

3. **Phase 3: Compact parser** (~200 LOC)
   - `compact.py`: `Schedule:Compact` DSL parser
   - `Through:`, `For:`, `Until:` syntax
   - Day type matching (Weekdays, Weekends, Holidays, Design days)

4. **Phase 4: Schedule:File** (~100 LOC)
   - `file.py`: CSV parsing with `FileSystem` protocol
   - Column/separator handling
   - Value caching

5. **Phase 5: Integration** (~80 LOC)
   - `evaluate.py`: Dispatch + interpolation logic
   - `series.py`: `to_series()` pandas wrapper
   - `IDFDocument` convenience methods

Total estimate: ~650 LOC + tests

## Design Decisions

### 1. Holidays

Holidays are extracted from `RunPeriodControl:SpecialDays` objects in the document.

```python
--8<-- "docs/snippets/design/schedule-evaluator/1_holidays.py"
```

Day types from `RunPeriodControl:SpecialDays`:
- `Holiday` - Standard holiday
- `CustomDay1`, `CustomDay2` - User-defined special day types

### 2. Design Days

Expose `SummerDesignDay` and `WinterDesignDay` via explicit parameter:

```python
--8<-- "docs/snippets/design/schedule-evaluator/2_design_days.py"
```

### 3. Interpolation

Match EnergyPlus interpolation behavior exactly. E+ has two modes:

**"No" (default)**: Step function - value at each interval applies until the next interval.
```
Schedule interval: 0-15min=0.0, 15-30min=0.5
Timestep 10min: value = 0.0
Timestep 20min: value = 0.5
```

**"Average"**: Linear interpolation when timestep doesn't align with intervals.
```
Schedule interval: 0-15min=0.0, 15-30min=0.5
Timestep 10min: value = 0.0
Timestep 20min: value = 0.25  (average of 0.0 and 0.5)
```

```python
--8<-- "docs/snippets/design/schedule-evaluator/3_interpolation.py"
```

### 4. Schedule:File Support

Support external CSV files via the existing `FileSystem` protocol:

```python
--8<-- "docs/snippets/design/schedule-evaluator/4_schedulefile_support.py"
```

**Schedule:File fields:**
| Field | Description |
|-------|-------------|
| Name | Schedule name |
| Schedule Type Limits Name | Reference to ScheduleTypeLimits |
| File Name | Path to CSV file (relative or absolute) |
| Column Number | 1-based column index in CSV |
| Rows to Skip at Top | Header rows to skip |
| Number of Hours of Data | Usually 8760 (or 8784 for leap year) |
| Column Separator | Comma, Tab, Space, Semicolon |
| Interpolate to Timestep | "No" or "Average" |
| Minutes per Item | 60, 30, 15, 10, 5, or 1 |

**CSV parsing with FileSystem:**
```python
--8<-- "docs/snippets/design/schedule-evaluator/4_schedulefile_support_2.py"
```

**Caching:** Schedule:File data should be cached after first read to avoid repeated I/O:

```python
--8<-- "docs/snippets/design/schedule-evaluator/4_schedulefile_support_3.py"
```
