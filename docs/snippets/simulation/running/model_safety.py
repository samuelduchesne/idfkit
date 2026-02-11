model = load_idf("building.idf")
original_count = len(model)

result = simulate(model, weather)

# Model unchanged
assert len(model) == original_count
assert "Output:SQLite" not in model
