def nearest(
    self,
    latitude: float,
    longitude: float,
    *,
    limit: int = 5,
    max_distance_km: float | None = None,
    country: str | None = None,
) -> list[SpatialResult]:
