from idfkit.schedules import to_series, plot_schedule

# Convert to pandas Series with datetime index
series = to_series(schedule, year=2024, document=doc)
print(series.describe())

# Quick visualization
plot_schedule(schedule, year=2024, document=doc)
