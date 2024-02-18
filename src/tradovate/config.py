import sys
import redis
import yaml
import logging
from logging.handlers import RotatingFileHandler
from src.constants import CONFIG_FILE, LOG_FILE, LOG_FILE_ERR, LOGGER_NAME
from src.utils.general import csv_to_list

URLs = {
    "DEMO": "https://demo.tradovateapi.com/v1",
    "LIVE": "https://live.tradovateapi.com/v1",
    "MD": "wss://md.tradovateapi.com/v1/websocket",
    "WS_DEMO": "wss://demo.tradovateapi.com/v1/websocket",
    "WS_LIVE": "wss://live.tradovateapi.com/v1/websocket",
}

CONFIG: dict = {}
logger = logging.getLogger(LOGGER_NAME)


def load_config(temp_conf: dict = None) -> dict:
    """
    Checks to see if configuration file is already loaded. If not then it reads it from the config file.
    :param temp_conf: dictionary of configuration file to check to see if it is already loaded or not
    :return Dictionary of configuration file we loaded from CONFIG_FILE or copied if it was already loaded
    """
    if not temp_conf:
        with open(CONFIG_FILE, 'r') as yml_file:
            temp_conf = yaml.load(yml_file, Loader=yaml.Loader)
            temp_conf['WEBHOOK']['actions'] = csv_to_list(temp_conf['WEBHOOK']['actions'])
            temp_conf['WEBHOOK']['port'] = temp_conf['WEBHOOK'].get('port', 80)
    return temp_conf


def load_logger(temp_conf: dict):
    """
    Load logger to be used in other classes
    :param temp_conf: A dictionary of the configuration file
    """
    log_level = temp_conf.get('debug_level', 'INFO').upper()
    log_backups = temp_conf.get('log_backups', 1)
    # Log to standard output for debugging if this constant is set to True
    std_out_handler = logging.StreamHandler(sys.stdout)
    handlers = [std_out_handler]
    # Main Logfile handler
    main_handler = RotatingFileHandler(LOG_FILE, maxBytes=5242880, backupCount=log_backups,
                                       encoding="UTF-8")
    main_handler.setLevel(level=log_level)

    # Error logfile handler
    error_handler = RotatingFileHandler(LOG_FILE_ERR, maxBytes=5242880, backupCount=log_backups,
                                        encoding="UTF-8")
    error_handler.setLevel(level=logging.WARNING)
    handlers.extend([main_handler, error_handler])

    formatter = logging.Formatter(
        fmt='%(asctime)s | %(filename)s:%(funcName)s:%(lineno)s | %(levelname)s |  %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    for h in handlers:
        h.setFormatter(formatter)
        logger.addHandler(h)
    # Set Log Level
    logger.setLevel(log_level)

    logger.debug("***** Logger Loaded *****")

    return logger


# Load config on import if we need to
CONFIG = load_config(CONFIG)

# Load our logging settings
load_logger(CONFIG)

redis_client = redis.Redis(host=CONFIG['REDIS'].get("redis_host", "localhost"),
                           port=CONFIG['REDIS'].get("redis_port", 6379),
                           username=CONFIG['REDIS'].get("redis_user", "default"),
                           password=CONFIG['REDIS'].get("redis_passwd", None),
                           decode_responses=True)

# Authorization Dictionary for Tradovate
to_auth_dict: dict = {
    "name": CONFIG['TO'].get("to_name"),
    "password": CONFIG['TO'].get('to_password'),
    "appId": CONFIG['TO'].get('to_appid'),
    "appVersion": "1.0",
    "cid": CONFIG['TO'].get('to_cid'),
    "sec": CONFIG['TO'].get('to_sec'),
    "deviceId": CONFIG['TO'].get('to_devid', 1)
}