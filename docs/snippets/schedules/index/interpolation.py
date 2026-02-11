from idfkit.schedules import values

# Step function (default) - value changes at each Until time
step_values = values(schedule, timestep=4, interpolation="no")

# Linear interpolation between values
smooth_values = values(schedule, timestep=4, interpolation="average")
