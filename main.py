from __future__ import (absolute_import, division, print_function, unicode_literals)
from src.config import CONFIG, logger
import src.webhooks.webhook_listener_lite as wl
import time


def main(seconds: int = 0):
    if seconds > 0:
        for _ in range(seconds):
            time.sleep(1)
    else:
        while True:
            time.sleep(1)


if __name__ == "__main__":
    # Start Bot
    # logger.debug(f'Configuration:\n{CONFIG}')
    # if CONFIG['TO']['to_env'].upper() == 'LIVE':
    #     logger.warning("**** Running in LIVE Mode **** Press [Enter] to Continue...")
    #     input()
    wh_server = None
    try:
        wh_server = wl.WHListener(port=CONFIG['WEBHOOK']['port'], auto_start=True)
        # Run Main Code
        main()
    except Exception as e:
        logger.exception(e)
    finally:
        wh_server.stop()
