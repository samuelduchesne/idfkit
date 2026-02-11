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
