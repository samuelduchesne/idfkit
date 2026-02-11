result = simulate(model, weather)

# model is unchanged — Output:SQLite was added to a copy
assert "Output:SQLite" not in model
