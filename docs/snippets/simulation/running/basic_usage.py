from idfkit import load_idf
from idfkit.simulation import simulate

model = load_idf("building.idf")
result = simulate(model, "weather.epw")

print(f"Success: {result.success}")
print(f"Runtime: {result.runtime_seconds:.1f}s")
print(f"Output directory: {result.run_dir}")
