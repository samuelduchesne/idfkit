from idfkit.simulation import simulate
from idfkit.simulation.progress_bars import tqdm_progress

with tqdm_progress(
    desc="Annual run",
    bar_format="{l_bar}{bar:30}| {n:.0f}% [{elapsed}<{remaining}]",
    leave=False,  # Remove bar after completion
    position=1,  # For nested bars
) as cb:
    result = simulate(model, "weather.epw", annual=True, on_progress=cb)
