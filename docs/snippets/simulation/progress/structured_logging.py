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
