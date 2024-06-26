import sys
import os
import redis
import yaml
import logging
from logging.handlers import RotatingFileHandler
from src.constants import CONFIG_FILE, CONFIG_ACTIONS_DIR, CONFIG_ALERTS_DIR, LOG_DIR, LOG_FILE, LOG_FILE_ERR, LOGGER_NAME
from src.utils.general import csv_to_list

CONFIG: dict = {}
# : dict = {}
# Travovate Authentication dictionary
to_auth_dict: dict = {}
# Redis Client Currently only used by Tradovate
redis_client: redis.Redis | None = None
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
            temp_conf['ACTIONS'] = csv_to_list(temp_conf['ACTIONS'])
            temp_conf['ALERTS'] = csv_to_list(temp_conf.get('ALERTS', ''))
            temp_conf['WEBHOOK']['port'] = temp_conf['WEBHOOK'].get('port', 80)
    return temp_conf


def load_logger(temp_conf: dict):
    """
    Load logger to be used in other classes
    :param temp_conf: A dictionary of the configuration file
    """
    if os.path.isdir(LOG_DIR) is False:
        os.mkdir(LOG_DIR)
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


def load_handlers_conf(conf: dict, handler_name: str):
    """
    Load Action and Event Handlers Configuration
    :param conf: Main Configuration dictionary
    :param handler_name: 'ACTIONS' or 'ALERTS'
    :return Dictionary of Handlers Configuration
    """
    temp_hl_dict = {}
    handler_dir = CONFIG_ACTIONS_DIR if handler_name.upper() == 'ACTIONS' else CONFIG_ALERTS_DIR
    for handler in conf[handler_name.upper()]:
        handler_file = os.path.join(handler_dir, f"{handler}.yaml")
        if os.path.exists(handler_file):
            logger.info(f"[{handler_name.upper()}/{handler}] - Loading configuration.")
            with open(handler_file, 'r') as yml_file:
                temp_hl_conf = yaml.load(yml_file, Loader=yaml.Loader)
                temp_hl_dict[handler] = temp_hl_conf
        else:
            logger.warning(f"[{handler_name.upper()}/{handler}] - No configuration file found at [{handler_file}], "
                           f"so no configuration will be loaded for this {handler_name}. If there is no configuration "
                           f"required for this handler for example a print_action, then this OK to ignore this.")
    return temp_hl_dict


# Load config on import if we need to
CONFIG = load_config(CONFIG)
# Load our logging settings
load_logger(CONFIG)
CONFIG_ACTIONS = load_handlers_conf(conf=CONFIG, handler_name='ACTIONS')
CONFIG_ALERTS = load_handlers_conf(conf=CONFIG, handler_name='ALERTS')

if 'tradovate' in CONFIG_ACTIONS.keys():
    logger.debug("Loading Tradovate Authentication and Redis Settings")
    to_conf = ['tradovate']
    to_auth_dict = {
        "password": to_conf['TO'].get('to_password'),
        "appId": to_conf['TO'].get('to_appid'),
        "appVersion": "1.0",
        "cid": to_conf['TO'].get('to_cid'),
        "sec": to_conf['TO'].get('to_sec'),
        "deviceId": to_conf['TO'].get('to_devid', 1)
    }
    redis_client = redis.Redis(host=to_conf['REDIS'].get("redis_host", "localhost"),
                               port=to_conf['REDIS'].get("redis_port", 6379),
                               username=to_conf['REDIS'].get("redis_user", "default"),
                               password=to_conf['REDIS'].get("redis_passwd", None),
                               decode_responses=True)
