import logging
import json
from datetime import datetime


def setup_logging():
    logging.basicConfig(filename="app.log", level=logging.INFO, format="%(message)s")
    return logging.getLogger(__name__)


def log_info(message, **kwargs):
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "level": "info",
        "event": message,
        **kwargs,
    }
    logging.info(json.dumps(log_data, indent=2))


def log_error(message, **kwargs):
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "level": "error",
        "event": message,
        **kwargs,
    }
    logging.error(json.dumps(log_data, indent=2))


def log_warning(message, **kwargs):
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "level": "warning",
        "event": message,
        **kwargs,
    }
    logging.warning(json.dumps(log_data, indent=2))
