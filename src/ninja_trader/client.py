import os
import threading
import time
import logging

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
    NAME = None

    def __init__(self, mon_con: bool = False, alerts: list = None):
        """
        :param mon_con: True = Monitor NinjaTrader Connection, False = Do NOT Monitor NT connection
        :param alerts: [Optional] List of Alert Objects to use
        """
        super().__init__()
        self.NAME = self.__class__.__name__
        self._nt_mon_thread = None
        self._nt_mon_kill_thread = threading.Event()
        self._alerts: list = alerts
        if self.is_connected(True) is False:
            logger.warning("Couldn't connect to ATI Interface. Make sure NT8 is open and that 'Tools -> Options -> "
                           "Automated Trading Interface -> General -> AT Interface' to make sure that checkbox is "
                           "checked.")
        else:
            logger.info("Successfully Connected to NinjaTrader Client.")
        self.accounts: list = csv_to_list(self.CONF['ACCOUNTS'])
        if mon_con:
            self.monitor_nt_conn()

    def alert(self, msg: str, subject: str = None, log_level: int = logging.ERROR):
        """
        Send an Alert through the alert Message Objects
        :param msg: Message of Alert to be sent
        :param subject: Subject of Message
        :param log_level: Optional: Default is to log as an Error, but may also use values like logging.INFO
        """
        subject = subject or self.NAME
        if self._alerts is not None:
            for alert in self._alerts:
                alert.run(subject=subject, msg=msg)
        logger.log(level=log_level, msg=f"[{subject}]: {msg}")

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

    def monitor_nt_conn(self, enable: bool = True):
        """
        Monitor NinjaTrader Connection, so we can be alerted or something else when we can't connect to NT Desktop App
        :param enable: True = Monitor NT's connection, False = Disable Monitoring the Connection
        """
        if enable:
            if self._alerts is None:
                logger.warning("You have no Alerts set, so this will only write to log file if something goes wrong.")
            logger.info('Monitoring NinjaTrader Desktop Client Connection.')
            self._nt_mon_thread = create_a_thread(func=self._nt_monitor, name='nt_hearbeat')
        elif self._nt_mon_thread is not None:  # If enable == False & thread is Alive, then kill it
            logger.info("Disabling Monitored Connection to NinjaTrader Desktop Client.")
            self._nt_mon_kill_thread.set()
            self._nt_mon_thread.join()
            self._nt_mon_thread = None

    def _nt_monitor(self, check_secs: int = 30, retry_count: int = 2):
        """
        Check Heartbeat of NinjaTrader to make sure we didn't lose connection!
        :param check_secs: Check to see if we're connected every this many seconds.
        :param retry_count: [Optional] Amount of times to Retry before Alerting!
        """
        count = 0
        while not self._nt_mon_kill_thread.is_set():
            time.sleep(check_secs)
            if not self.is_connected(show_msg_box=False):
                count += 1
                if count < retry_count:
                    logger.warning(
                        f"[{self.NAME}] - App is no longer able to connect to NinjaTrader! Retry Count: [{count}/{retry_count}]")
                elif count == retry_count:
                    self.alert(
                        msg=f"App is no longer able to connect to NinjaTrader after [{count}/{retry_count}] attempts!"
                            f" Manual invention is required!",
                        subject=f"{self.NAME}: ERROR")
            elif count >= retry_count:
                count = 0
                self.alert(msg="Good news we regained connection to the Ninja Trader Client!", subject=f"{self.NAME}: Reconnected", log_level=logging.INFO)

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
            self.alert(
                msg=f'ERROR: Code: {ret_val}, [{account}] - [MARKET ORDER] Order ID: {order_id} Symbol: {symbol}, Side: {side.upper()}, Quantity: {amount}, comment: [{comment}]',
                subject=self.NAME)
        return ret_val


if __name__ == "__main__":
    nt_client = NTClient(mon_con=True)
    # print(f"NinjaTrader Methods: {dir(Client())}")
    for _ in range(180):
        time.sleep(1)

    nt_client.monitor_nt_conn(enable=False)

    # nt_client.place_market_order(symbol='MNQ MAR24', side='BUY', amount=1, comment='test order',
    # order_id='test_order')
    print(f"Current Position is: {nt_client.get_cur_pos('MNQ JUN24')}")
    nt_client = None
    # print(f"Orders: {nt_client.Orders('DEMO2284144')}")
    # print("Finished Testing NT Client")
