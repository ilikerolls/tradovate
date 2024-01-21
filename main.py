from __future__ import (absolute_import, division, print_function, unicode_literals)
import src.tradovate as td
from src.tradovate.config import CONFIG, logger
import src.webhooks.webhook_listener_lite as wl
from src.utils.general import Singleton
import time

class TOBot(metaclass=Singleton):
    def __init__(self):
        # Holds Client & Session Data
        #self.client = td.Client()
        #self.account_api = td.Accounting(self.client.session)
        #self.account_list = self.account_api.account_list()
        #self.orders_api = td.Orders()
        for _ in range(0, 60):
            time.sleep(1)



#if __name__ == "__main__":
# Start Bot
logger.debug(f'Configuration:\n{CONFIG}')
wh_server = wl.WHListener(port=8000, auto_start=True)
try:
    # Run Main Code
    TO_BOT = TOBot()
except Exception as e:
    logger.exception(e)
finally:
    wh_server.stop()
