from idfkit.weather import DesignDayManager

# Parse a DDY file
ddm = DesignDayManager("chicago.ddy")

# Print summary
print(ddm.summary())

# Apply design days to model
added = ddm.apply_to_model(
    model,
    heating="99.6%",
    cooling="1%",
)
print(f"Added {len(added)} design days")
