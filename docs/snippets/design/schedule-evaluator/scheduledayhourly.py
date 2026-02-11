def evaluate_day_hourly(obj: IDFObject, dt: datetime) -> float:
    hour = dt.hour  # 0-23
    field_name = f"Hour {hour + 1}"  # "Hour 1" through "Hour 24"
    return float(obj[field_name])
