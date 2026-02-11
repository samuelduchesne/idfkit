import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as tmp:
    # Download all files for a run
    for obj in fs.glob("run-001", "*"):
        data = fs.read_bytes(obj)
        local_path = Path(tmp) / Path(obj).name
        local_path.write_bytes(data)

    # Now use local result
    result = SimulationResult.from_directory(tmp)
    # Multiple queries without network calls
