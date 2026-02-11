from idfkit.exceptions import NoDesignDaysError

try:
    ddm = DesignDayManager("incomplete.ddy")
    ddm.apply_to_model(model, heating="99.6%", cooling="1%")
except NoDesignDaysError as e:
    print(f"Missing design days: {e}")
