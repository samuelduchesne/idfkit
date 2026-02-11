from idfkit import load_idf
from idfkit.simulation import simulate

model = load_idf("building.idf")
result = simulate(model, "weather.epw", annual=True, on_progress="tqdm")
