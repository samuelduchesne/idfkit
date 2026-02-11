# Check if a result would hit cache
key = cache.compute_key(model, weather, design_day=True)
if cache.contains(key):
    print("Would be a cache hit")

# Clear all cached results
cache.clear()
