#!/usr/bin/env python
"""
Benchmark idfkit against eppy for common EnergyPlus IDF operations.

This script generates a realistic IDF file and benchmarks both tools on:
- Parsing/loading IDF files
- Querying objects by type
- Querying a single object by name
- Adding new objects
- Modifying object fields
- Writing IDF to string

Usage:
    uv run --group benchmark python benchmarks/bench.py
"""

from __future__ import annotations

import gc
import json
import os
import platform
import sys
import tempfile
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

NUM_ZONES = 500
NUM_MATERIALS = 100
NUM_SURFACES = 1000
ITERATIONS = 10  # Repeat each benchmark
RESULTS_FILE = Path(__file__).parent / "results.json"

# The V24.1 IDD template is fetched from EnergyPlus source and patched at
# runtime.  We cache the result under a .gitignored directory so repeated
# runs are fast.
_IDD_CACHE_DIR = Path(__file__).parent / ".cache"
_IDD_FILE = _IDD_CACHE_DIR / "Energy+V24_1_0.idd"
_IDD_TEMPLATE_URL = (
    "https://raw.githubusercontent.com/NREL/EnergyPlus/"
    "v24.1.0/idd/Energy%2B.idd.in"
)


# ---------------------------------------------------------------------------
# IDD download helper
# ---------------------------------------------------------------------------


def _ensure_idd() -> Path:
    """Download and cache the EnergyPlus V24.1 IDD if not already present."""
    if _IDD_FILE.exists():
        return _IDD_FILE

    import subprocess

    _IDD_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"  Downloading EnergyPlus V24.1 IDD template from GitHub ...")
    result = subprocess.run(
        ["curl", "-sL", _IDD_TEMPLATE_URL],
        capture_output=True,
        check=True,
    )
    # Replace CMake template variables with actual version numbers
    content = result.stdout.decode("latin-1")
    content = (
        content.replace("${CMAKE_VERSION_MAJOR}", "24")
        .replace("${CMAKE_VERSION_MINOR}", "1")
        .replace("${CMAKE_VERSION_PATCH}", "0")
        .replace("${CMAKE_VERSION_BUILD}", "9d7789a3ac")
    )
    _IDD_FILE.write_text(content, encoding="latin-1")
    print(f"  Cached IDD at {_IDD_FILE} ({_IDD_FILE.stat().st_size / 1024:.0f} KB)")
    return _IDD_FILE


# ---------------------------------------------------------------------------
# Test‑file generation
# ---------------------------------------------------------------------------


def generate_test_idf(
    num_zones: int = NUM_ZONES,
    num_materials: int = NUM_MATERIALS,
    num_surfaces: int = NUM_SURFACES,
) -> str:
    """Generate a realistic IDF file for benchmarking.

    Uses Version 24.1 with a downloaded V24.1 IDD for eppy and idfkit's
    bundled V24.1 epJSON schema.
    """
    lines: list[str] = []
    lines.append("Version, 24.1;")
    lines.append("")

    # Zones
    for i in range(num_zones):
        lines.append(
            f"Zone,\n"
            f"  Zone_{i},                !- Name\n"
            f"  0,                       !- Direction of Relative North {{deg}}\n"
            f"  {i * 10},               !- X Origin {{m}}\n"
            f"  0,                       !- Y Origin {{m}}\n"
            f"  0,                       !- Z Origin {{m}}\n"
            f"  1,                       !- Type\n"
            f"  1;                       !- Multiplier"
        )
        lines.append("")

    # Materials
    for i in range(num_materials):
        lines.append(
            f"Material,\n"
            f"  Material_{i},            !- Name\n"
            f"  MediumRough,             !- Roughness\n"
            f"  0.{i + 1:03d},              !- Thickness {{m}}\n"
            f"  0.16,                    !- Conductivity {{W/m-K}}\n"
            f"  784,                     !- Density {{kg/m3}}\n"
            f"  830,                     !- Specific Heat {{J/kg-K}}\n"
            f"  0.9;                     !- Thermal Absorptance"
        )
        lines.append("")

    # Constructions
    for i in range(num_materials):
        lines.append(
            f"Construction,\n"
            f"  Construction_{i},        !- Name\n"
            f"  Material_{i};            !- Outside Layer"
        )
        lines.append("")

    # Building surfaces
    for i in range(num_surfaces):
        zone_idx = i % num_zones
        const_idx = i % num_materials
        lines.append(
            f"BuildingSurface:Detailed,\n"
            f"  Surface_{i},             !- Name\n"
            f"  Wall,                    !- Surface Type\n"
            f"  Construction_{const_idx},!- Construction Name\n"
            f"  Zone_{zone_idx},         !- Zone Name\n"
            f"  Outdoors,                !- Outside Boundary Condition\n"
            f"  ,                        !- Outside Boundary Condition Object\n"
            f"  SunExposed,              !- Sun Exposure\n"
            f"  WindExposed,             !- Wind Exposure\n"
            f"  0.5,                     !- View Factor to Ground\n"
            f"  4,                       !- Number of Vertices\n"
            f"  0, 0, 3,                 !- Vertex 1 X/Y/Z\n"
            f"  0, 0, 0,                 !- Vertex 2 X/Y/Z\n"
            f"  10, 0, 0,                !- Vertex 3 X/Y/Z\n"
            f"  10, 0, 3;                !- Vertex 4 X/Y/Z"
        )
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Timing helper
# ---------------------------------------------------------------------------


def bench(func, iterations: int = ITERATIONS) -> dict[str, float]:
    """Run *func* multiple times and return timing statistics (seconds)."""
    times: list[float] = []
    for _ in range(iterations):
        gc.collect()
        gc.disable()
        t0 = time.perf_counter()
        func()
        t1 = time.perf_counter()
        gc.enable()
        times.append(t1 - t0)
    return {
        "min": min(times),
        "mean": sum(times) / len(times),
        "max": max(times),
        "times": times,
    }


# ---------------------------------------------------------------------------
# idfkit benchmarks
# ---------------------------------------------------------------------------


def benchmark_idfkit(idf_path: str) -> dict[str, dict[str, float]]:
    """Benchmark idfkit on all operations."""
    from idfkit import load_idf, new_document, write_idf

    results: dict[str, dict[str, float]] = {}

    # 1. Parse / Load ----------------------------------------------------------
    def load() -> None:
        load_idf(idf_path)

    results["Load IDF file"] = bench(load)
    # keep a model around for the rest of the benchmarks
    model = load_idf(idf_path)

    # 2. Query all objects of a type -------------------------------------------
    def query_type() -> None:
        _ = list(model["Zone"])

    results["Get all objects by type"] = bench(query_type, iterations=ITERATIONS * 10)

    # 3. Query single object by name -------------------------------------------
    def query_name() -> None:
        _ = model["Zone"]["Zone_250"]

    results["Get single object by name"] = bench(query_name, iterations=ITERATIONS * 10)

    # 4. Add 100 new objects ---------------------------------------------------
    def add_objects() -> None:
        doc = new_document(version=(24, 1, 0))
        for i in range(100):
            doc.add("Zone", f"NewZone_{i}", {"x_origin": float(i * 5)})

    results["Add 100 objects"] = bench(add_objects)

    # 5. Modify fields on all zones --------------------------------------------
    def modify_fields() -> None:
        for zone in model["Zone"]:
            zone.x_origin = 99.0

    results["Modify fields (all zones)"] = bench(modify_fields)

    # 6. Write to string -------------------------------------------------------
    def write() -> None:
        write_idf(model, None)

    results["Write IDF to string"] = bench(write)

    return results


# ---------------------------------------------------------------------------
# eppy benchmarks
# ---------------------------------------------------------------------------


def benchmark_eppy(idf_path: str) -> dict[str, dict[str, float]]:
    """Benchmark eppy on all operations."""
    from eppy.modeleditor import IDF

    # Use V24.1 IDD (downloaded on first run, then cached)
    idd_path = _ensure_idd()
    IDF.setiddname(str(idd_path))

    results: dict[str, dict[str, float]] = {}

    # 1. Parse / Load ----------------------------------------------------------
    def load() -> None:
        IDF(idf_path)

    results["Load IDF file"] = bench(load)
    # keep a model around
    idf = IDF(idf_path)

    # 2. Query all objects of a type -------------------------------------------
    def query_type() -> None:
        _ = idf.idfobjects["Zone"]

    results["Get all objects by type"] = bench(query_type, iterations=ITERATIONS * 10)

    # 3. Query single object by name -------------------------------------------
    def query_name() -> None:
        _ = idf.getobject("Zone", "Zone_250")

    results["Get single object by name"] = bench(query_name, iterations=ITERATIONS * 10)

    # 4. Add 100 new objects ---------------------------------------------------
    def add_objects() -> None:
        tmp_idf = IDF(idf_path)
        for i in range(100):
            tmp_idf.newidfobject("Zone", Name=f"NewZone_{i}")

    results["Add 100 objects"] = bench(add_objects)

    # 5. Modify fields on all zones --------------------------------------------
    def modify_fields() -> None:
        for zone in idf.idfobjects["Zone"]:
            zone.X_Origin = 99.0

    results["Modify fields (all zones)"] = bench(modify_fields)

    # 6. Write to string -------------------------------------------------------
    def write() -> None:
        idf.idfstr()

    results["Write IDF to string"] = bench(write)

    return results


# ---------------------------------------------------------------------------
# Chart generation
# ---------------------------------------------------------------------------


def generate_chart(
    idfkit_results: dict[str, dict[str, float]],
    eppy_results: dict[str, dict[str, float]],
    output_path: Path,
) -> None:
    """Generate a horizontal bar chart comparing idfkit vs eppy."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker

    operations = list(idfkit_results.keys())
    idfkit_times = [idfkit_results[op]["min"] for op in operations]
    eppy_times = [eppy_results[op]["min"] for op in operations]

    # Compute speedup factors
    speedups = [e / i if i > 0 else float("inf") for i, e in zip(idfkit_times, eppy_times)]

    fig, axes = plt.subplots(
        len(operations), 1, figsize=(10, 1.6 * len(operations) + 1.2), constrained_layout=True
    )
    if len(operations) == 1:
        axes = [axes]

    colors = {"idfkit": "#4C78A8", "eppy": "#E45756"}

    for idx, (ax, op) in enumerate(zip(axes, operations)):
        ik_t = idfkit_times[idx]
        ep_t = eppy_times[idx]
        max_t = max(ik_t, ep_t)

        bars = ax.barh(
            ["eppy", "idfkit"],
            [ep_t, ik_t],
            color=[colors["eppy"], colors["idfkit"]],
            height=0.55,
            edgecolor="white",
            linewidth=0.5,
        )

        # Add time labels on bars
        for bar, t in zip(bars, [ep_t, ik_t]):
            label = _format_time(t)
            x_pos = bar.get_width()
            # Place label outside bar if bar is narrow
            if x_pos < max_t * 0.35:
                ax.text(
                    x_pos + max_t * 0.02,
                    bar.get_y() + bar.get_height() / 2,
                    label,
                    va="center",
                    ha="left",
                    fontsize=10,
                    fontweight="bold",
                    color="#333",
                )
            else:
                ax.text(
                    x_pos - max_t * 0.02,
                    bar.get_y() + bar.get_height() / 2,
                    label,
                    va="center",
                    ha="right",
                    fontsize=10,
                    fontweight="bold",
                    color="white",
                )

        ax.set_title(
            f"{op}  ({speedups[idx]:.1f}x faster)" if speedups[idx] > 1.05 else op,
            fontsize=11,
            fontweight="bold",
            loc="left",
            pad=8,
        )
        ax.set_xlim(0, max_t * 1.15)
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: _format_time(x)))
        ax.tick_params(axis="x", labelsize=9)
        ax.tick_params(axis="y", labelsize=10)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.invert_yaxis()

    fig.suptitle(
        f"idfkit vs eppy  \u2014  {NUM_ZONES} zones, {NUM_MATERIALS} materials, "
        f"{NUM_SURFACES} surfaces ({_total_objects()} total objects)",
        fontsize=13,
        fontweight="bold",
        y=1.01,
    )

    fig.savefig(str(output_path), dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Chart saved to {output_path}")


def _total_objects() -> int:
    return NUM_ZONES + NUM_MATERIALS + NUM_MATERIALS + NUM_SURFACES  # zones + materials + constructions + surfaces


def _format_time(seconds: float) -> str:
    """Human-readable time string."""
    if seconds < 1e-6:
        return f"{seconds * 1e9:.0f}ns"
    if seconds < 1e-3:
        return f"{seconds * 1e6:.1f}\u00b5s"
    if seconds < 1:
        return f"{seconds * 1e3:.1f}ms"
    return f"{seconds:.2f}s"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print("=" * 60)
    print("  idfkit performance benchmark")
    print("=" * 60)
    print(f"  Python  : {sys.version.split()[0]}")
    print(f"  Platform: {platform.system()} {platform.machine()}")
    print(f"  Objects : {NUM_ZONES} zones, {NUM_MATERIALS} materials,")
    print(f"            {NUM_MATERIALS} constructions, {NUM_SURFACES} surfaces")
    print(f"            ({_total_objects()} total)")
    print(f"  Iters   : {ITERATIONS}")
    print("=" * 60)

    # Generate test IDF
    print("\nGenerating test IDF file...")
    idf_text = generate_test_idf()
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".idf", delete=False)
    tmp.write(idf_text)
    tmp.close()
    idf_path = tmp.name
    file_size = os.path.getsize(idf_path)
    print(f"  File size: {file_size / 1024:.1f} KB")

    try:
        # Benchmark idfkit
        print("\nBenchmarking idfkit ...")
        idfkit_results = benchmark_idfkit(idf_path)
        for op, r in idfkit_results.items():
            print(f"  {op:30s}  {_format_time(r['min']):>10s}")

        # Benchmark eppy
        print("\nBenchmarking eppy ...")
        eppy_results = benchmark_eppy(idf_path)
        for op, r in eppy_results.items():
            print(f"  {op:30s}  {_format_time(r['min']):>10s}")

        # Summary
        print("\n" + "=" * 60)
        print("  Speedup (idfkit vs eppy) — higher is better for idfkit")
        print("=" * 60)
        for op in idfkit_results:
            ik = idfkit_results[op]["min"]
            ep = eppy_results[op]["min"]
            speedup = ep / ik if ik > 0 else float("inf")
            faster = "idfkit" if speedup > 1 else "eppy"
            factor = speedup if speedup > 1 else 1 / speedup
            print(f"  {op:30s}  {factor:6.1f}x  ({faster})")

        # Save results
        output = {
            "metadata": {
                "python": sys.version.split()[0],
                "platform": f"{platform.system()} {platform.machine()}",
                "num_zones": NUM_ZONES,
                "num_materials": NUM_MATERIALS,
                "num_surfaces": NUM_SURFACES,
                "total_objects": _total_objects(),
                "file_size_bytes": file_size,
                "iterations": ITERATIONS,
            },
            "idfkit": {op: {"min": r["min"], "mean": r["mean"]} for op, r in idfkit_results.items()},
            "eppy": {op: {"min": r["min"], "mean": r["mean"]} for op, r in eppy_results.items()},
        }
        with open(RESULTS_FILE, "w") as f:
            json.dump(output, f, indent=2)
        print(f"\nResults saved to {RESULTS_FILE}")

        # Generate chart
        chart_path = Path(__file__).parent.parent / "docs" / "assets" / "benchmark.png"
        chart_path.parent.mkdir(parents=True, exist_ok=True)
        generate_chart(idfkit_results, eppy_results, chart_path)

    finally:
        os.unlink(idf_path)


if __name__ == "__main__":
    main()
