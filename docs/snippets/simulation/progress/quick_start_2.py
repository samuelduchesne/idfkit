from idfkit.simulation import simulate, SimulationProgress


def on_progress(event: SimulationProgress) -> None:
    if event.percent is not None:
        print(f"[{event.percent:5.1f}%] {event.phase}: {event.message}")
    else:
        print(f"[  ?  ] {event.phase}: {event.message}")


result = simulate(model, "weather.epw", annual=True, on_progress=on_progress)
