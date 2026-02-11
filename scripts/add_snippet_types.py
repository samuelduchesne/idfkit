"""Add type preambles and section markers to extracted doc snippet files.

For each .py snippet under docs/snippets/:
1. Parse with `ast` to find names used but never defined
2. Map undefined names to type annotations and/or imports
3. Write the file with: imports + stubs (hidden) then section-marked original code
4. Update the corresponding markdown include to use section syntax

This makes all snippets type-checkable by pyright in basic mode while
keeping the docs rendering unchanged (only the section content is shown).
"""

from __future__ import annotations

import ast
import builtins
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
SNIPPETS_DIR = DOCS_DIR / "snippets"

# ---------------------------------------------------------------------------
# Mapping: variable name -> type annotation string
# These get emitted as: name: Type = ...  # type: ignore[assignment]
# ---------------------------------------------------------------------------
VARIABLE_STUBS: dict[str, str] = {
    # Core idfkit types
    "model": "IDFDocument",
    "doc": "IDFDocument",
    "idf": "IDFDocument",
    "variant": "IDFDocument",
    "expanded": "IDFDocument",
    "model1": "IDFDocument",
    "model2": "IDFDocument",
    "variant1": "IDFDocument",
    "variant2": "IDFDocument",
    "variants": "list[IDFDocument]",
    "model_variants": "list[IDFDocument]",
    # IDF objects
    "zone": "IDFObject",
    "surface": "IDFObject",
    "office": "IDFObject",
    "obj": "IDFObject",
    "schedule": "IDFObject",
    "construction": "IDFObject",
    "people_obj": "IDFObject",
    "occupancy": "IDFObject",
    "dd_obj": "IDFObject",
    "htg": "IDFObject | None",
    "clg": "IDFObject | None",
    "removed": "IDFObject",
    # Simulation
    "result": "SimulationResult",
    "result1": "SimulationResult",
    "result2": "SimulationResult",
    "batch": "BatchResult",
    "batch1": "BatchResult",
    "batch2": "BatchResult",
    "jobs": "list[SimulationJob]",
    "job": "SimulationJob",
    "job_id": "str",
    "config": "EnergyPlusConfig",
    # SQL / output
    "sql": "SQLResult | None",
    "ts": "TimeSeriesResult",
    "ts_sizing": "TimeSeriesResult",
    "ts1": "TimeSeriesResult",
    "ts2": "TimeSeriesResult",
    "errors": "ErrorReport",
    "html": "HTMLResult | None",
    "csv_result": "CSVResult | None",
    "variables": "OutputVariableIndex | None",
    # Weather
    "index": "StationIndex",
    "station": "WeatherStation",
    "files": "WeatherFiles",
    "downloader": "WeatherDownloader",
    "ddm": "DesignDayManager",
    "location": "Any",
    "my_stations": "list[Any]",
    # File system / cache
    "cache": "SimulationCache",
    "fs": "S3FileSystem",
    "s3_fs": "S3FileSystem",
    # Primitives
    "weather": "str",
    "weather_path": "str",
    "html_string": "str",
    "lat": "float",
    "lon": "float",
    "num_cases": "int",
    "addresses": "list[str]",
    "weather_meta": "dict[str, Any]",
    "weather_files": "dict[str, WeatherFiles]",
    "results": "list[SimulationResult | None]",
    "added": "list[IDFObject]",
    "validation": "ValidationResult",
    # eppy compat (migration docs)
    "idf_string": "str",
    "referrers": "list[IDFObject]",
    "surfaces": "list[IDFObject]",
    "names": "list[str]",
    "key": "CacheKey",
    "cached_result": "SimulationResult | None",
    "fig": "Any",
    "table": "Any",
    "data": "Any",
    "my_model": "IDFDocument",
    "zone_names": "list[str]",
    "dt": "Any",
    # Third-party aliases (stubbed as Any since not installed)
    "plt": "Any",
    "pd": "Any",
    "px": "Any",
    "np": "Any",
    "tqdm": "Any",
    "websocket": "Any",
    "redis_client": "Any",
    "message_queue": "Any",
    # Schedule evaluator internals (design doc pseudo-code)
    "find_week_for_date": "Any",
    "evaluate_week": "Any",
    "evaluate_day": "Any",
    "field_name_for_index": "Any",
    "day_schedule_type": "Any",
    "week_type": "Any",
    "parse_time": "Any",
}

# ---------------------------------------------------------------------------
# Mapping: type name -> module to import from
# ---------------------------------------------------------------------------
TYPE_IMPORTS: dict[str, str] = {
    "IDFDocument": "idfkit",
    "IDFObject": "idfkit",
    "IDFCollection": "idfkit",
    "Vector3D": "idfkit",
    "ValidationResult": "idfkit",
    "SimulationResult": "idfkit.simulation",
    "SimulationJob": "idfkit.simulation",
    "BatchResult": "idfkit.simulation",
    "SimulationEvent": "idfkit.simulation",
    "SQLResult": "idfkit.simulation",
    "CSVResult": "idfkit.simulation",
    "HTMLResult": "idfkit.simulation",
    "ErrorReport": "idfkit.simulation",
    "ErrorMessage": "idfkit.simulation",
    "OutputVariableIndex": "idfkit.simulation",
    "TimeSeriesResult": "idfkit.simulation",
    "TabularRow": "idfkit.simulation",
    "VariableInfo": "idfkit.simulation",
    "EnvironmentInfo": "idfkit.simulation",
    "EnergyPlusConfig": "idfkit.simulation",
    "SimulationCache": "idfkit.simulation",
    "CacheKey": "idfkit.simulation",
    "S3FileSystem": "idfkit.simulation",
    "FileSystem": "idfkit.simulation",
    "LocalFileSystem": "idfkit.simulation",
    "SimulationProgress": "idfkit.simulation",
    "ProgressParser": "idfkit.simulation",
    "StationIndex": "idfkit.weather",
    "WeatherStation": "idfkit.weather",
    "WeatherDownloader": "idfkit.weather",
    "WeatherFiles": "idfkit.weather",
    "SpatialResult": "idfkit.weather",
    "SearchResult": "idfkit.weather",
    "DesignDayManager": "idfkit.weather",
    "DesignDayType": "idfkit.weather",
}

# ---------------------------------------------------------------------------
# Mapping: function/class name -> (module, name) for preamble imports
# These are added when the name is used but not imported in the snippet.
# ---------------------------------------------------------------------------
FUNCTION_IMPORTS: dict[str, str] = {
    # idfkit top-level
    "load_idf": "idfkit",
    "load_epjson": "idfkit",
    "new_document": "idfkit",
    "write_idf": "idfkit",
    "write_epjson": "idfkit",
    "validate_document": "idfkit",
    "RangeError": "idfkit",
    "IDFDocument": "idfkit",
    "IDFObject": "idfkit",
    # Simulation
    "simulate": "idfkit.simulation",
    "async_simulate": "idfkit.simulation",
    "simulate_batch": "idfkit.simulation",
    "async_simulate_batch": "idfkit.simulation",
    "async_simulate_batch_stream": "idfkit.simulation",
    "find_energyplus": "idfkit.simulation",
    "expand_objects": "idfkit.simulation",
    "run_slab_preprocessor": "idfkit.simulation",
    "run_basement_preprocessor": "idfkit.simulation",
    "SimulationResult": "idfkit.simulation",
    "SimulationJob": "idfkit.simulation",
    "SimulationCache": "idfkit.simulation",
    "SimulationError": "idfkit.simulation",
    "BatchResult": "idfkit.simulation",
    "SQLResult": "idfkit.simulation",
    "HTMLResult": "idfkit.simulation",
    "ErrorReport": "idfkit.simulation",
    "S3FileSystem": "idfkit.simulation",
    "FileSystem": "idfkit.simulation",
    "LocalFileSystem": "idfkit.simulation",
    "EnergyPlusConfig": "idfkit.simulation",
    "OutputVariableIndex": "idfkit.simulation",
    "SimulationProgress": "idfkit.simulation",
    "ProgressParser": "idfkit.simulation",
    # Weather
    "StationIndex": "idfkit.weather",
    "WeatherDownloader": "idfkit.weather",
    "WeatherStation": "idfkit.weather",
    "DesignDayManager": "idfkit.weather",
    "DesignDayType": "idfkit.weather",
    "geocode": "idfkit.weather",
    "GeocodingError": "idfkit.weather",
    "apply_ashrae_sizing": "idfkit.weather",
    # Schedules
    "evaluate": "idfkit.schedules",
    "values": "idfkit.schedules",
    "to_series": "idfkit.schedules",
    "get_holidays": "idfkit.schedules",
    "plot_schedule": "idfkit.schedules",
    "DayType": "idfkit.schedules",
    "Interpolation": "idfkit.schedules",
    # Geometry
    "Vector3D": "idfkit",
    "calculate_surface_area": "idfkit.geometry",
    "calculate_surface_tilt": "idfkit.geometry",
    "calculate_surface_azimuth": "idfkit.geometry",
    "calculate_zone_volume": "idfkit.geometry",
    "calculate_zone_height": "idfkit.geometry",
    "calculate_zone_ceiling_area": "idfkit.geometry",
    "translate_building": "idfkit.geometry",
    "rotate_building": "idfkit.geometry",
    # Exceptions
    "NoDesignDaysError": "idfkit",
    # Plotting
    "MatplotlibBackend": "idfkit.simulation",
    "PlotlyBackend": "idfkit.simulation",
    "plot_temperature_profile": "idfkit.simulation",
    "plot_energy_balance": "idfkit.simulation",
    "plot_comfort_hours": "idfkit.simulation",
    # Stdlib (added to preamble as imports)
    "Path": "pathlib",
    "datetime": "datetime",
    "date": "datetime",
    "time": "datetime",
    "asyncio": "asyncio",
    "dataclass": "dataclasses",
    "Enum": "enum",
    # typing module
    "Any": "typing",
    "Literal": "typing",
    "Callable": "typing",
    "Protocol": "typing",
}

# Names to always ignore (builtins, common patterns, third-party)
BUILTIN_NAMES = set(dir(builtins)) | {
    "TypeVar",
    "TYPE_CHECKING",
    "self",
    "cls",
    "args",
    "kwargs",
    "True",
    "False",
    "None",
    "__name__",
    "__file__",
    "property",
    "staticmethod",
    "classmethod",
    "lru_cache",
    # Third-party names we can't resolve (optional deps)
    "FastAPI",
    "app",
    "Progress",
    "progress",
    "task",
    "IDF",  # eppy
    "json_functions",  # eppy
    "readhtml",  # eppy
    "ContainerClient",  # azure
    "ipywidgets",
    # Common loop/lambda vars
    "i",
    "r",
    "v",
    "col",
    "row",
    "err",
    "warn",
    "event",
    "insulation",
    "city",
    "address",
    "status",
    "pct",
    "label",
    "callback",
}


def _collect_target_names(node: ast.AST) -> set[str]:
    """Extract all Name nodes from an assignment target."""
    return {t.id for t in ast.walk(node) if isinstance(t, ast.Name)}


def _collect_func_arg_names(node: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    """Extract all argument names from a function definition."""
    names = {arg.arg for arg in node.args.args + node.args.posonlyargs + node.args.kwonlyargs}
    if node.args.vararg:
        names.add(node.args.vararg.arg)
    if node.args.kwarg:
        names.add(node.args.kwarg.arg)
    return names


def _collect_import_names(tree: ast.Module) -> set[str]:
    """Extract all imported names from the AST."""
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                names.add(alias.asname if alias.asname else alias.name)
    return names


def _names_defined_by(node: ast.AST) -> set[str]:
    """Return names defined by a single AST node."""
    if isinstance(node, (ast.Import, ast.ImportFrom)):
        return {alias.asname if alias.asname else alias.name for alias in node.names}
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return {node.name} | _collect_func_arg_names(node)
    if isinstance(node, ast.ClassDef):
        return {node.name}
    if isinstance(node, ast.For):
        return _collect_target_names(node.target)
    if isinstance(node, ast.With):
        names: set[str] = set()
        for item in node.items:
            if item.optional_vars:
                names |= _collect_target_names(item.optional_vars)
        return names
    if isinstance(node, ast.ExceptHandler) and node.name:
        return {node.name}
    if isinstance(node, ast.comprehension):
        return _collect_target_names(node.target)
    return set()


def _collect_defined_and_used(tree: ast.Module) -> tuple[set[str], set[str]]:
    """Walk AST and collect defined and used name sets."""
    defined: set[str] = set()
    used: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            if isinstance(node.ctx, (ast.Store, ast.Del)):
                defined.add(node.id)
            elif isinstance(node.ctx, ast.Load):
                used.add(node.id)
        else:
            defined |= _names_defined_by(node)

    return defined, used


def find_undefined_names(source: str) -> set[str]:
    """Find names referenced but never defined in the source."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()

    defined, used = _collect_defined_and_used(tree)
    undefined = used - defined - BUILTIN_NAMES

    # Also include names that are used AND defined if they're in VARIABLE_STUBS
    # (handles "used before conditionally assigned" patterns like `if index.check(): index = ...`)
    imported = _collect_import_names(tree)
    for name in used & defined - imported - BUILTIN_NAMES:
        if name in VARIABLE_STUBS:
            undefined.add(name)

    return undefined


def extract_type_names(annotation: str) -> set[str]:
    """Extract type names from an annotation string like 'list[IDFObject]'."""
    return set(re.findall(r"[A-Z]\w+", annotation))


def _resolve_stubs_and_imports(
    undefined: set[str],
) -> tuple[dict[str, str], dict[str, set[str]]]:
    """Resolve undefined names into variable stubs and import groups."""
    stubs: dict[str, str] = {}
    imports_by_module: dict[str, set[str]] = {}

    for name in sorted(undefined):
        if name in VARIABLE_STUBS:
            stubs[name] = VARIABLE_STUBS[name]
        elif name in FUNCTION_IMPORTS:
            module = FUNCTION_IMPORTS[name]
            imports_by_module.setdefault(module, set()).add(name)

    # Collect type imports needed by stub annotations
    for annotation in stubs.values():
        for type_name in extract_type_names(annotation):
            if type_name in TYPE_IMPORTS:
                module = TYPE_IMPORTS[type_name]
                imports_by_module.setdefault(module, set()).add(type_name)
        if "Any" in annotation:
            imports_by_module.setdefault("typing", set()).add("Any")

    return stubs, imports_by_module


def build_preamble(undefined: set[str], source: str) -> str:
    """Build the import + stub preamble for a snippet file."""
    stubs, imports_by_module = _resolve_stubs_and_imports(undefined)

    if not stubs and not imports_by_module:
        return ""

    lines: list[str] = ["from __future__ import annotations", ""]

    for module in sorted(imports_by_module):
        names = sorted(imports_by_module[module])
        lines.append(f"from {module} import {', '.join(names)}")

    if imports_by_module:
        lines.append("")

    for name in sorted(stubs):
        lines.append(f"{name}: {stubs[name]} = ...  # type: ignore[assignment]")

    if stubs:
        lines.append("")

    return "\n".join(lines)


def process_snippet(snippet_path: Path) -> bool:
    """Add preamble and section markers to a snippet file.

    Returns True if the file was modified.
    """
    original = snippet_path.read_text()

    # Skip files that already have section markers
    if "# --8<-- [start:example]" in original:
        return False

    # Find undefined names
    undefined = find_undefined_names(original)

    # Build preamble
    preamble = build_preamble(undefined, original)

    # Assemble the new file content
    parts: list[str] = []
    if preamble:
        parts.append(preamble)
    else:
        parts.append("from __future__ import annotations\n\n")

    parts.append("# --8<-- [start:example]\n")
    parts.append(original.rstrip("\n"))
    parts.append("\n# --8<-- [end:example]\n")

    snippet_path.write_text("".join(parts))
    return True


def update_markdown_includes(docs_dir: Path) -> int:
    """Update all --8<-- includes to use :example section syntax.

    Returns the number of includes updated.
    """
    count = 0
    for md_path in sorted(docs_dir.rglob("*.md")):
        content = md_path.read_text()
        # Match: --8<-- "docs/snippets/...py" (without :example already)
        updated = re.sub(
            r'--8<-- "(docs/snippets/[^"]+\.py)"',
            r'--8<-- "\1:example"',
            content,
        )
        if updated != content:
            md_path.write_text(updated)
            count += updated.count(":example") - content.count(":example")
    return count


def main() -> None:
    snippets = sorted(SNIPPETS_DIR.rglob("*.py"))
    print(f"Found {len(snippets)} snippet files")

    modified = 0
    for path in snippets:
        if process_snippet(path):
            modified += 1

    print(f"Added preambles to {modified} files")

    count = update_markdown_includes(DOCS_DIR)
    print(f"Updated {count} markdown includes to use :example sections")


if __name__ == "__main__":
    main()
