class Interpolation(Enum):
    NO = "no"           # Step function (default)
    AVERAGE = "average" # Linear interpolation
    LINEAR = "linear"   # Alias for AVERAGE

def values(
    schedule: IDFObject,
    year: int = 2024,
    timestep: int = 1,  # per hour
    interpolation: Interpolation = Interpolation.NO,
    ...
) -> list[float]:
    """
    Generate schedule values with specified interpolation.

    The interpolation mode affects how values are computed when the
    evaluation timestep doesn't align with the schedule's native intervals.
    """
