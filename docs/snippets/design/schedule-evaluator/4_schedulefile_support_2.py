from idfkit.simulation.fs import FileSystem


def _read_schedule_csv(
    file_path: str,
    column: int,
    skip_rows: int,
    separator: str,
    fs: FileSystem,
) -> list[float]:
    """Read schedule values from CSV using FileSystem protocol."""
    text = fs.read_text(file_path)
    lines = text.strip().split("\n")[skip_rows:]
    sep = {"Comma": ",", "Tab": "\t", "Space": " ", "Semicolon": ";"}[separator]
    values = []
    for line in lines:
        cols = line.split(sep)
        values.append(float(cols[column - 1]))  # 1-based index
    return values
