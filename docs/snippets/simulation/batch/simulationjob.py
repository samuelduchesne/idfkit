from idfkit.simulation import SimulationJob

job = SimulationJob(
    model=my_model,  # Required: IDFDocument
    weather="weather.epw",  # Required: Path to weather file
    label="case-001",  # Optional: Label for progress reporting
    output_dir="./output/case1",  # Optional: Output directory
    design_day=True,  # Optional: Design-day-only
    annual=False,  # Optional: Annual simulation
    timeout=3600.0,  # Optional: Max runtime in seconds
)
