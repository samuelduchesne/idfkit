from idfkit.simulation import simulate

result = simulate(model, "weather.epw", design_day=True)
print(f"Outputs in: {result.run_dir}")
