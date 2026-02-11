added = ddm.apply_to_model(
    model,
    heating="99.6%",
    cooling="1%",
)

# Or use the convenience function (takes a WeatherStation, not a path)
added = apply_ashrae_sizing(model, station, standard="90.1")
