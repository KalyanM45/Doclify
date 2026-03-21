import os
import json
import subprocess
from pathlib import Path
from doclify.utils.logger import get_logger

# Initialize the logger
logger = get_logger(__name__)

CACHE_DIR = Path(".doclify")
CACHE_FILE = CACHE_DIR / "cache.json"

def load_cache():
    try:
        logger.info(f"Loading cache from {CACHE_FILE}")
        if CACHE_FILE.exists():
            logger.info("Cache found")
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        
        logger.info("Cache not found, returning empty cache")
        return {"files": {}}
    except Exception:
        logger.error("Error loading cache", exc_info=True)
        return {"files": {}}

def clean_cache(cache, valid_files):
    """
    Removes entries from cache["files"] that are not in the valid_files list.
    Normalizes all paths before comparison.
    """
    if "files" not in cache:
        return cache
    
    valid_paths = {os.path.normpath(f) for f in valid_files}
    logger.info(f"Cleaning cache. Valid files count: {len(valid_paths)}")
    
    cleaned_files = {}
    for k, v in cache["files"].items():
        if os.path.normpath(k) in valid_paths:
            cleaned_files[k] = v
        else:
            logger.info(f"Removing stale key from cache: {k}")
            
    cache["files"] = cleaned_files
    return cache

def save_cache(cache):
    target_dir = CACHE_DIR
    
    if os.name == "nt":
        # Windows: hidden folder (can be dot-prefixed or not, usually . is fine)
        target_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(["attrib", "+H", str(target_dir)])
    else:
        # Linux / macOS: ensure dot-prefixed folder
        if not target_dir.name.startswith("."):
            target_dir = target_dir.with_name("." + target_dir.name)
        target_dir.mkdir(parents=True, exist_ok=True)
    
    target_file = target_dir / "cache.json"
    logger.info(f"Saving cache to {target_file}")
    target_file.write_text(json.dumps(cache, indent=2), encoding="utf-8")
