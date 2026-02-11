import json
import logging
from dataclasses import asdict
from idfkit.simulation import simulate, SimulationProgress

# Configure for JSON-structured cloud logging
logger = logging.getLogger("energyplus.progress")


def on_progress(event: SimulationProgress) -> None:
    # asdict() makes SimulationProgress JSON-serializable
    logger.info(json.dumps(asdict(event)))


result = simulate(model, "weather.epw", on_progress=on_progress)
