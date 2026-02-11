# Compute key
key = cache.compute_key(model, weather)

# Check cache
cached_result = cache.get(key)
if cached_result is not None:
    print("Cache hit!")
else:
    # Run simulation
    result = simulate(model, weather)

    # Store in cache (only successful results)
    cache.put(key, result)
