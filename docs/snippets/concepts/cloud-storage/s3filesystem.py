from idfkit.simulation import S3FileSystem

fs = S3FileSystem(
    bucket="my-simulations",
    prefix="batch-42/",
)

result = simulate(model, weather, output_dir="run-001", fs=fs)
