from redis.exceptions import TimeoutError, AuthenticationError

from src.config import logger
from src.utils.general import Singleton
import src.tradovate as td


class TOBot(metaclass=Singleton):
    def __init__(self):
        try:
            # Holds Client & Session Data
            self.client = td.Client()
            self.account_api = td.Accounting(self.client.session)
            self.account_list = self.account_api.account_list()
            self.orders_api = td.Orders()
        except(TimeoutError, AuthenticationError) as e:
            logger.exception(
                f"Couldn't connect to Redis! Most likely the Redis Server hasn't been started yet or Credentials are "
                f"wrong? Error:\n{e}")
            # raise Exception("Redis Error")
        except Exception as e:
            logger.exception(f"Couldn't Connect to Tradovate:\n{e}")
