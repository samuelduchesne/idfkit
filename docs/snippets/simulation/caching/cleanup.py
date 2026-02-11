# Clear everything
cache.clear()

# Or manually delete specific entries
import shutil

shutil.rmtree(cache.cache_dir / "abc123...")
