def evaluate(
    schedule: IDFObject,
    dt: datetime,
    document: IDFDocument | None = None,
    day_type: DayType = DayType.NORMAL,
    fs: FileSystem | None = None,
) -> float:
    """
    Get schedule value at a specific datetime.

    Args:
        schedule: An IDF schedule object (any supported type)
        dt: The datetime to evaluate
        document: Required for schedules that reference others (Year, Week)
                  If None, extracted from schedule._document
        day_type: Override with design day schedule (for sizing calcs)
        fs: FileSystem for Schedule:File (default: LocalFileSystem)

    Returns:
        The schedule value as a float

    Raises:
        ScheduleEvaluationError: If schedule type unsupported or malformed
    """
