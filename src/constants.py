import os
from pathlib import Path

# Top/Parent directory to the Bot
ROOT_DIR: str = str(Path(__file__).parent.parent)
CONFIG_FILE = os.path.join(ROOT_DIR, "config.yml")
# Log Files
LOGGER_NAME = 'TO_BOT'
LOG_FILE = os.path.join(ROOT_DIR, "logs", f"{LOGGER_NAME}.log")
LOG_FILE_ERR = os.path.join(ROOT_DIR, "logs", f"{LOGGER_NAME}.log")
