from idfkit.weather import apply_ashrae_sizing

# Apply standard design conditions (downloads DDY from station automatically)
added = apply_ashrae_sizing(
    model,
    station,
    standard="90.1",  # ASHRAE 90.1 criteria
)
