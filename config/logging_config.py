import logging
import json
from datetime import datetime


def setup_logging():
    logging.basicConfig(filename="app.log", level=logging.INFO, format="%(message)s")
    return logging.getLogger(__name__)


def log_info(message, **kwargs):
    log_data = {
        "event": message,
        "timestamp": datetime.now().isoformat(),
        "level": "info",
        **kwargs,
    }
    logging.info(json.dumps(log_data, indent=2))
