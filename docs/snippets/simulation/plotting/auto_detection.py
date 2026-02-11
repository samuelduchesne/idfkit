from idfkit.simulation import get_default_backend

backend = get_default_backend()
print(type(backend).__name__)  # MatplotlibBackend or PlotlyBackend
