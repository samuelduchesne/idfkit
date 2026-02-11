from idfkit.simulation import LocalFileSystem

fs = LocalFileSystem()  # This is the default
result = simulate(model, weather)  # Implicitly uses LocalFileSystem
