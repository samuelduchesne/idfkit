import shutil
from idfkit.weather.download import default_cache_dir

shutil.rmtree(default_cache_dir())
