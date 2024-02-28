import os.path
import re

from src.config import logger
from src.utils.general import csv_to_list, string_to_date
from src.webhooks.handlers.action import Action


class NinjatraderAction(Action):
    """
    Writes OIF(Order Instruction Files) files to NinjaTrader directory for processing. Commands:
    https://ninjatrader.com/support/helpGuides/nt8/NT%20HelpGuide%20English.html?order_instruction_files_oif.htm
    OIFs must be written to the folder 'My Documents\<NinjaTrader Folder>\incoming" and be named oif*.txt'
    """

    def __init__(self, action_name: str):
        """
        :param action_name: Name given to Action by Action Manager
        """
        super().__init__(action_name=action_name)
        self.oif_count: int = 0
        # Load csv string of accounts to an iterable list to send actions to
        self.accounts: list = csv_to_list(self.conf['ACCOUNTS'])

    def process_out_files(self):
        """
        TODO: Process status update files put out by NinjaTrader
        https://ninjatrader.com/support/helpGuides/nt8/NT%20HelpGuide%20English.html?order_instruction_files_oif.htm
        Order Status File Format: Sim101_Reversal_Trade_02-18-24-17_00_6.699.txt
        """
        pass

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
        market_cmd = f'PLACE;<ACCOUNT>;{self.tr_symbol(symbol)};{side.upper()};{amount};MARKET;;;GTC;;{order_id};;'
        # Full path to file to write Market Order Commands to
        out_file = os.path.join(self.conf['OIF']['IN_DIR'], f'oif_{self.oif_count}.txt')
        # Add Command to file for each account
        with open(out_file, "w") as f_out:
            for account in self.accounts:
                new_market_cmd = re.sub(r'<ACCOUNT>', account, market_cmd)
                f_out.write(f'{new_market_cmd}\n')
                logger.info(
                    f"[{self.action_name}] - CMD: [{new_market_cmd}] to file: [{out_file}], comment: [{comment}]")
        self.oif_count += 1

    def run(self, *args, **kwargs):
        """
        Custom run method. Add your custom logic here.
        """
        super().run(*args, **kwargs)
        try:
            if self.data['o_type'].upper() == 'MARKET':
                self.place_market_order(symbol=str(self.data['sym']), side=str(self.data['side']),
                                        amount=int(self.data['amount']), comment=str(self.data.get('comment', None)),
                                        order_id=self.data.get('sig_id', None))
        except ValueError as ve:
            logger.warning(f"Couldn't find either an order type or another required parameter in webhook:\n{ve}")

    def tr_symbol(self, sym: str) -> str:
        """
        Translate symbol
        :param sym: Symbol to translate ex: MNQ1! -> MNQ
        :return:
        """
        if sym in self.conf['SYM_TR'].keys():
            return string_to_date(self.conf['SYM_TR'][sym])
        return sym
