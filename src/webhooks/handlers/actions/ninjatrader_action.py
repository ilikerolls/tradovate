from src.webhooks.handlers.action import Action
from src.config import logger
from src.utils.general import string_to_date, csv_to_list
from src.ninja_trader.client import NTClient


class NinjatraderAction(Action):
    """
    Sends Commands to NinjaTrader API such as Market Orders when called by the ActionManager for ex: from a Webhook
    """

    def __init__(self, action_name: str):
        """
        :param action_name: Name given to Action by Action Manager
        """
        super().__init__(action_name=action_name)
        self.ntc = NTClient()
        self.nt_accounts: list = csv_to_list(self.conf['ACCOUNTS'])

    def get_nt_synched_tv(self, symbol: str) -> dict:
        """
        Get a list of NinjaTrader account's Market Position Sizes that are in Synchronization with TradingView's Open
        Positions
        :param symbol: Symbol from TradingView to Check on NinjaTrader
        :return A Dict of each value: of NinjaTrader Account with key: True = NT position acct In synch with TV,
        False = NT Position NOT in synch with TV ex: {'DEMO2284144': True, 'Sim101': False}
        """
        # Cast to Strings purely for comparison reasons incase either is a float in the future instead of an int
        tv_prev_pos = str(self.data['prev_pos_size'])
        nt_positions: dict = self.ntc.get_cur_pos(symbol=symbol)
        nt_is_synch_accts: dict = {
            nt_acct: str(pos) == tv_prev_pos
            for [nt_acct, pos] in nt_positions.items()
        }
        return nt_is_synch_accts

    def run(self, *args, **kwargs):
        """
        Process a Webhook Command and send it to NinjaTrader
        """
        super().run(*args, **kwargs)
        tr_symbol = self.tr_symbol(self.data['sym'])
        synched_nt_accts: dict = self.get_nt_synched_tv(symbol=tr_symbol)
        for [account, is_synched] in synched_nt_accts.items():
            if is_synched is True:  # Market Size Positions match between NT & TV
                try:
                    if self.data['o_type'].upper() == 'MARKET':
                        self.ntc.place_market_order(account=account, symbol=tr_symbol,
                                                    side=str(self.data['side']), amount=int(self.data['amount']),
                                                    comment=str(self.data.get('comment', None)),
                                                    order_id=self.data.get('sig_id', None))
                except ValueError as ve:
                    logger.warning(
                        f"Couldn't find either an order type or another required parameter in webhook:\n{ve}")
            else:
                logger.warning(f"NinjaTrader Account: [{account}] NT Symbols: [{tr_symbol}] doesn't have same Market "
                               f"Position as TradingView's Previous Position size of {self.data['prev_pos_size']}. NOT "
                               f"Processing Webhook:\n{self.data}")

    def tr_symbol(self, sym: str) -> str:
        """
        Translate symbol
        :param sym: Symbol to translate ex: MNQ1! -> MNQ
        :return:
        """
        if 'SYM_TR' in self.conf.keys() and sym in self.conf['SYM_TR'].keys():
            return string_to_date(self.conf['SYM_TR'][sym])
        return sym
