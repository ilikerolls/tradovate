from __future__ import (absolute_import, division, print_function, unicode_literals)
from src.tradovate.config import CONFIG, logger
import src.webhooks.webhook_listener_lite as wl
import time

from src.tradovate.to_bot import TOBot


def main():
    # to = TOBot()
    for _ in range(60):
        time.sleep(1)


if __name__ == "__main__":
    # Start Bot
    logger.debug(f'Configuration:\n{CONFIG}')
    wh_server = None
    try:
        wh_server = wl.WHListener(port=8000, auto_start=True)
        # Run Main Code
        main()
    except Exception as e:
        logger.exception(e)
    finally:
        wh_server.stop()
