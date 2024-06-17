import os
import re

from src.config import logger, CONFIG_ACTIONS
from src.utils.general import csv_to_list, string_to_date


class NTClientOIF:
    """
    Ninja Trader's OIF(Order Instruction Files) API Interface
    https://ninjatrader.com/support/helpGuides/nt8/NT%20HelpGuide%20English.html?order_instruction_files_oif.htm
    """
    CONF = CONFIG_ACTIONS['ninjatrader']

    def __init__(self):
        self.oif_count: int = 0
        self.accounts: list = csv_to_list(self.CONF['ACCOUNTS'])

    def place_market_order(self, symbol: str, side: str, amount: int, comment: str = None, order_id: str = None):
        """
        Place a Market Order - via OIF(Order Instruction File Interface) aka oif*.txt file
        https://ninjatrader.com/support/helpGuides/nt8/NT%20HelpGuide%20English.html?commands_and_valid_parameters.htm
        :param symbol: Name of Symbol to Order with
        :param side: 'BUY' = Place a Buy Market Order, 'SELL' = Place a sell Market Order
        :param amount: How many contracts do you want to buy/sell? Documentation says it MUST be an integer?
        :param comment: Optional: A Comment to Add to Order
        :param order_id: Optional: Assign an Order ID to Order
        """
        # market_cmd = 'PLACE;<ACCOUNT>;<INSTRUMENT>;<ACTION>;<QTY>;<ORDER TYPE>;[LIMIT PRICE];[STOP PRICE];<TIF>;[OCO ID];[ORDER ID];[STRATEGY];[STRATEGY ID]'
        market_cmd = f'PLACE;<ACCOUNT>;{symbol};{side.upper()};{amount};MARKET;;;GTC;;{order_id};;'
        # Full path to file to write Market Order Commands to
        out_file = os.path.join(self.CONF['OIF']['IN_DIR'], f'oif_{self.oif_count}.txt')
        # Add Command to file for each account
        with open(out_file, "w") as f_out:
            for account in self.accounts:
                new_market_cmd = re.sub(r'<ACCOUNT>', account, market_cmd)
                f_out.write(f'{new_market_cmd}\n')
                logger.info(f"CMD: [{new_market_cmd}] to file: [{out_file}], comment: [{comment}]")
        self.oif_count += 1

    def process_out_files(self):
        """
        TODO: Process status update files put out by NinjaTrader
        https://ninjatrader.com/support/helpGuides/nt8/NT%20HelpGuide%20English.html?order_instruction_files_oif.htm
        Order Status File Format: Sim101_Reversal_Trade_02-18-24-17_00_6.699.txt
        """
        pass
