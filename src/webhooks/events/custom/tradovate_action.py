from redis.exceptions import TimeoutError, AuthenticationError

from src.webhooks.events.action import Action
from src.tradovate.config import logger
from src.tradovate.to_bot import TOBot


class TradovateAction(Action):
    def __init__(self):
        super().__init__()
        try:
            self.to = TOBot()
        except(TimeoutError, AuthenticationError) as e:
            logger.exception(
                f"Couldn't connect to Redis! Most likely the Redis Server hasn't been started yet or Credentials are "
                f"wrong? Error:\n{e}")
            # raise Exception("Redis Error")
        except Exception as e:
            logger.exception(f"Couldn't Connect to Tradovate:\n{e}")
            # raise Exception("Tradovate Error")

    def place_market_order(self, symbol: str, side: str, amount: int, comment: str = None, order_id: str = None):
        """
        Place a Market Order - https://api.tradovate.com/#operation/placeOrder
        :param symbol: Name of Symbol to Order with
        :param side: 'Buy' = Place a Buy Market Order, 'Sell' = Place a sell Market Order
        :param amount: How many contracts do you want to buy/sell? Documentation says it MUST be an integer?
        :param comment: Optional: A Comment to Add to Order
        :param order_id: Optional: Assign an Order ID to Order
        """
        logger.info(
            f"{self.name} - Placing Market Order: Order ID: {order_id}, symbol: {symbol}, side: {side}, amount: {amount}, comment: {comment}")
        self.to.orders_api.place_order(action=side, symbol=symbol, order_qty=amount, order_type='Market',
                                       cl_ord_id=order_id, text=comment)

    def run(self, *args, **kwargs):
        """
        Custom run method. Add your custom logic here.
        """
        super().run(*args, **kwargs)
        if self.data['action'].lower() == 'market_order':
            self.place_market_order(symbol=str(self.data['sym']), side=str(self.data['side']),
                                    amount=int(self.data['amount']), comment=str(self.data.get('comment', None)),
                                    order_id=self.data.get('sig_id', None))