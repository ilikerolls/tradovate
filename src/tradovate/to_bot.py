from src.utils.general import Singleton
import src.tradovate as td


class TOBot(metaclass=Singleton):
    def __init__(self):
        # Holds Client & Session Data
        self.client = td.Client()
        self.account_api = td.Accounting(self.client.session)
        self.account_list = self.account_api.account_list()
        self.orders_api = td.Orders()
