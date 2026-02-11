# Quick validation
result = simulate(model, weather, design_day=True)
if result.success:
    # Then run full annual
    result = simulate(model, weather, annual=True)
