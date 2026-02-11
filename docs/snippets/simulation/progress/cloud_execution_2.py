from dataclasses import asdict
import json


def on_progress(event: SimulationProgress) -> None:
    message_queue.publish(json.dumps(asdict(event)))
