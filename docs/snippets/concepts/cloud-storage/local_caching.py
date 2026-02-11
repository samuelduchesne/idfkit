import tempfile

# Download entire result directory
with tempfile.TemporaryDirectory() as tmp:
    # Copy from S3 to local
    for path in s3_fs.glob("run-001", "*"):
        data = s3_fs.read_bytes(path)
        local_path = Path(tmp) / Path(path).name
        local_path.write_bytes(data)

    # Use local result
    result = SimulationResult.from_directory(tmp)
    # Multiple queries without network calls
