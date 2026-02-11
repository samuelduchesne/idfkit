added = ddm.apply_to_model(
    model,
    heating="99.6%",
    cooling="1%",
    include_wet_bulb=True,  # Also add WB=>MDB cooling design day
)
