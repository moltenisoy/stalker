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

def diag_snapshot():
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "log_file": str(LOG_FILE),
    }