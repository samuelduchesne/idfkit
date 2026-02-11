import json
from idfkit.simulation import async_simulate, SimulationProgress


async def run_with_websocket(model, weather, websocket):
    """Run a simulation and forward progress over WebSocket."""

    async def on_progress(event: SimulationProgress) -> None:
        await websocket.send_text(
            json.dumps({
                "type": "simulation_progress",
                "phase": event.phase,
                "percent": event.percent,
                "message": event.message,
                "environment": event.environment,
            })
        )

    result = await async_simulate(model, weather, on_progress=on_progress)
    await websocket.send_text(
        json.dumps({
            "type": "simulation_complete",
            "success": result.success,
            "runtime": result.runtime_seconds,
        })
    )
    return result
