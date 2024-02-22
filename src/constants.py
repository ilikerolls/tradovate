import os
from pathlib import Path

# Top/Parent directory to the Bot
ROOT_DIR: str = str(Path(__file__).parent.parent)
CONFIG_DIR = os.path.join(ROOT_DIR, "configs")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.yml")
CONFIG_HANDLER_DIR = os.path.join(CONFIG_DIR, "handlers")
# Log Files
LOGGER_NAME = 'TO_BOT'
LOG_DIR = os.path.join(ROOT_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, f"{LOGGER_NAME}.log")
LOG_FILE_ERR = os.path.join(LOG_DIR, f"{LOGGER_NAME}_err.log")
# SSL Certificates
SSL_CRT = os.path.join(ROOT_DIR, "ssl", "cert.crt")
SSL_KEY = os.path.join(ROOT_DIR, "ssl", "cert.key")

TO_URLS = {
    "DEMO": "https://demo.tradovateapi.com/v1",
    "LIVE": "https://live.tradovateapi.com/v1",
    "MD": "wss://md.tradovateapi.com/v1/websocket",
    "WS_DEMO": "wss://demo.tradovateapi.com/v1/websocket",
    "WS_LIVE": "wss://live.tradovateapi.com/v1/websocket",
}