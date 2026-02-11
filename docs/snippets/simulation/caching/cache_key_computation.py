key = cache.compute_key(
    model,
    "weather.epw",
    design_day=True,
    annual=False,
)
print(f"Cache key: {key.hex_digest[:16]}...")
