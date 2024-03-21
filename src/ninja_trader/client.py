import os
import threading
import time

import clr
from src.config import CONFIG_HANDLERS, logger
from src.utils.general import csv_to_list, create_a_thread

# Add NT8 ATI Client DLL Library Reference
clr.AddReference(os.path.join(CONFIG_HANDLERS['ninjatrader_action']['DLL_DIR'], 'NinjaTrader.Client.DLL'))
from NinjaTrader.Client import Client


class NTClient(Client):
    """
    Ninjatrader API Client Wrapper class API Functions: https://ninjatrader.com/support/helpGuides/nt8/functions.htm
    API Parameters:
    https://ninjatrader.com/support/helpGuides/nt8/NT%20HelpGuide%20English.html?commands_and_valid_parameters.htm
    """
    CONF = CONFIG_HANDLERS['ninjatrader_action']

    def __init__(self):
        """
        :param mon_con: True = Monitor NinjaTrader Connection, False = Do NOT Monitor NT connection
        """
        super().__init__()
        self._nt_mon_thread = None
        self._nt_mon_kill_thread = threading.Event()
        self._alerts: list = []
        if self.is_connected(True) is False:
            logger.warning("Couldn't connect to ATI Interface. Make sure NT8 is open and that 'Tools -> Options -> "
                           "Automated Trading Interface -> General -> AT Interface' to make sure that checkbox is "
                           "checked.")
        else:
            logger.info("Successfully Connected to NinjaTrader Client.")
        self.accounts: list = csv_to_list(self.CONF['ACCOUNTS'])

    def __del__(self):
        """
        Clean Up any running threads, connection to NT, or anything else!
        """
        logger.info("Cleaning up Garbage!")
        self.monitor_nt_conn(enable=False)
        self.TearDown()  # Disconnect from Websocket

    def get_cur_pos(self, symbol: str) -> dict:
        """
        Get Current Market Position for a particular Symbol
        :param symbol: Symbol to check what our current position
        :return: Returns 0 for flat, negative value for short positive value for long in a dict form {'account':
        1} ex: { 'DEMO2284144': 1, 'Sim101': 0 } would mean DEMO2284144 is in a LONG position for this symbol and
        Sim101 is flat(no open positions)
        """
        return {
            account: self.MarketPosition(symbol, account)
            for account in self.accounts
        }

    def is_connected(self, show_msg_box: bool = True) -> bool:
        """
        Check to see if we can connect to ATI interface 0 = Connected, -1 = Cannot Connect to ATI Interface
        :param show_msg_box: True = Show a Message Box if not Connected to Alert user. False = Log Connection Error Only
        :return: True = Connected, False = Not Connected
        """
        return self.Connected(1 if show_msg_box else 0) == 0

    def monitor_nt_conn(self, enable: bool = True, alert: object = None):
        """
        Monitor NinjaTrader Connection, so we can be alerted or something else when we can't connect to NT Desktop App
        :param enable: True = Monitor NT's connection, False = Disable Monitoring the Connection
        :param alert: Optional Already Object to use
        """
        if enable:
            logger.info('Monitoring NinjaTrader Desktop Client Connection.')
            self._nt_mon_thread = create_a_thread(func=self._nt_monitor, name='nt_hearbeat', alert=alert)
        elif self._nt_mon_thread is not None:
            logger.info("Disabling Monitored Connection to NinjaTrader Desktop Client.")
            self._nt_mon_kill_thread.set()
            self._nt_mon_thread.join()
            self._nt_mon_thread = None

    def _nt_monitor(self, check_secs: int = 30, alert: object = None):
        """
        Check Heartbeat of NinjaTrader to make sure we didn't lose connection!
        :param check_secs: Check to see if we're connected every this many seconds.
        :param alert: [Optional] Already Object to use
        """
        retry_count = 2
        count = 0
        while not self._nt_mon_kill_thread.is_set():
            time.sleep(check_secs)
            if not self.is_connected(show_msg_box=False):
                count += 1
                logger.warning(f"App is no longer able to connect to NinjaTrader! Retry Count: [{count}]")
                if count >= retry_count:
                    if alert is not None:
                        alert.run(str(type(self).__name__), f"App is no longer able to connect to NinjaTrader after [{count}] attempts!")
                    logger.error(f"Tried to reconnect [{count}] times now! Giving up and Alerting Administrator")
                    break
                time.sleep(check_secs)

    def place_market_order(self, account: str, symbol: str, side: str, amount: int, comment: str = None,
                           order_id: str = None) -> int:
        """
        Place a Market Order - via OIF(Order Instruction File Interface) aka oif*.txt file
        :param account: Account Namer to Place Order For
        :param symbol: Name of Symbol to Order with
        :param side: 'BUY' = Place a Buy Market Order, 'SELL' = Place a sell Market Order
        :param amount: How many contracts do you want to buy/sell? Documentation says it MUST be an integer?
        :param comment: Optional: A Comment to Add to Order
        :param order_id: Optional: Assign an Order ID to Order
        """
        ret_val = self.Command(command='PLACE', account=account, instrument=symbol, action=side.upper(),
                               quantity=amount, orderType='MARKET', limitPrice=0.0, stopPrice=0.0,
                               timeInForce='GTC', oco='', orderId=order_id, tpl='', strategy='')
        if ret_val == 0:
            logger.info(
                f'[{account}] - [MARKET ORDER] Order ID: {order_id} Symbol: {symbol}, Side: {side.upper()}, Quantity: {amount}, comment: [{comment}]')
        else:
            logger.exception(
                f'ERROR: Code: {ret_val}, [{account}] - [MARKET ORDER] Order ID: {order_id} Symbol: {symbol}, Side: {side.upper()}, Quantity: {amount}, comment: [{comment}]')
        return ret_val


if __name__ == "__main__":
    nt_client = NTClient()
    nt_client.monitor_nt_conn(enable=True)
    # print(f"NinjaTrader Methods: {dir(Client())}")
    for _ in range(10):
        time.sleep(1)

    # nt_client.place_market_order(symbol='MNQ MAR24', side='BUY', amount=1, comment='test order',
    # order_id='test_order')
    print(f"Current Position is: {nt_client.get_cur_pos('MNQ JUN24')}")
    nt_client = None
    # print(f"Orders: {nt_client.Orders('DEMO2284144')}")
    # print("Finished Testing NT Client")
