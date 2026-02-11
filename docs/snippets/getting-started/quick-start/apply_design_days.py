from idfkit.weather import DesignDayManager

# Parse a DDY file and apply design days to your model
ddm = DesignDayManager("weather.ddy")
added = ddm.apply_to_model(
    model,
    heating="99.6%",
    cooling="1%",
    update_location=True,
)
print(f"Added {len(added)} design days")
