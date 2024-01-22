from src.webhooks.events.action import Action
from src.tradovate.config import logger
from src.tradovate.to_bot import TOBot


class TradovateAction(Action):
    def __init__(self):
        super().__init__()
        self.to = TOBot()

    def place_market_order(self, symbol: str, side: str, amount: int):
        """
        Place a Market Order - https://api.tradovate.com/#operation/placeOrder
        :param symbol: Name of Symbol to Order with
        :param side: 'Buy' = Place a Buy Market Order, 'Sell' = Place a sell Market Order
        :param amount: How many contracts do you want to buy/sell? Documentation says it MUST be an integer?
        """
        logger.info(f"{self.name} - Placing Market Order: symbol: {symbol}, side: {side}, amount: {amount}")
        self.to.orders_api.place_order(action=side.title(), symbol=symbol.upper(), order_qty=amount, order_type='Market')

    def run(self, *args, **kwargs):
        """
        Custom run method. Add your custom logic here.
        """
        super().run(*args, **kwargs)
        if self.data['action'].lower() == 'market_order':
            self.place_market_order(symbol=self.data['ticker'], side=self.data['side'], amount=self.data['amount'])
