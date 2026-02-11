class ScheduleFileCache:
    """Cache for Schedule:File CSV data."""

    _cache: dict[str, list[float]]  # file_path -> values

    def get_values(
        self,
        obj: IDFObject,
        fs: FileSystem,
        base_path: Path,
    ) -> list[float]:
        """Get cached values or read from file."""
