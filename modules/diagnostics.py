import logging
from pathlib import Path
from datetime import datetime

LOG_PATH = Path.home() / ".fastlauncher" / "logs"
LOG_PATH.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_PATH / "app.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

def log(msg: str):
    logging.info(msg)

def diag_snapshot(file_indexer=None):
    """Get diagnostic snapshot including indexer stats if available."""
    snapshot = {
        "timestamp": datetime.utcnow().isoformat(),
        "log_file": str(LOG_FILE),
    }
    
    if file_indexer:
        stats = file_indexer.get_stats()
        snapshot["file_indexer"] = {
            "files_indexed": stats.get("files_indexed", 0),
            "errors": stats.get("errors", 0),
            "last_run": datetime.fromtimestamp(stats["last_run"]).isoformat() if stats.get("last_run") else None,
            "roots": file_indexer.roots,
        }
    
    return snapshot