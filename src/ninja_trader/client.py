import os
import clr
from src.config import CONFIG_HANDLERS, logger
from src.utils.general import csv_to_list, string_to_date

# Add NT8 ATI Client DLL Library Reference
clr.AddReference(os.path.join(CONFIG_HANDLERS['ninjatrader']['DLL_DIR'], 'NinjaTrader.Client.DLL'))
from NinjaTrader.Client import Client


class NTClient(Client):
    """
    Ninjatrader API Client Wrapper class
    API Functions: https://ninjatrader.com/support/helpGuides/nt8/functions.htm
    API Parameters: https://ninjatrader.com/support/helpGuides/nt8/NT%20HelpGuide%20English.html?commands_and_valid_parameters.htm
    """
    NT_CONF = CONFIG_HANDLERS['ninjatrader']

    def __init__(self):
        super().__init__()
        if self.is_connected(True) is False:
            logger.warning("Couldn't connect to ATI Interface. Make sure NT8 is open and that 'Tools -> Options -> "
                           "Automated Trading Interface -> General -> AT Interface' to make sure that checkbox is "
                           "checked.")
        self.accounts: list = csv_to_list(self.NT_CONF['ACCOUNTS'])

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

    def place_market_order(self, account: str, symbol: str, side: str, amount: int, comment: str = None, order_id: str = None):
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


if __name__ == "__main__":
    nt_client = NTClient()
    print(f"NinjaTrader Methods: {dir(Client())}")
    # nt_client.place_market_order(symbol='MNQ MAR24', side='BUY', amount=1, comment='test order', order_id='test_order')
    print(f"Current Position is: {nt_client.get_cur_pos('MNQ MAR24')}")
    print(f"Orders: {nt_client.Orders('DEMO2284144')}")
    print("Finished Testing NT Client")
