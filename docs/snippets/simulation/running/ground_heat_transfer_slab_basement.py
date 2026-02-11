from idfkit.simulation import run_slab_preprocessor, run_basement_preprocessor

# Slab-on-grade foundation
expanded = run_slab_preprocessor(model, weather="weather.epw")

# Basement walls and floors
expanded = run_basement_preprocessor(model, weather="weather.epw")
