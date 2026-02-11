key = cache.compute_key(model, weather, design_day=True)

if cache.contains(key):
    print("Would be a cache hit")
else:
    print("Would be a cache miss")
