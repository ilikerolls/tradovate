from src.webhooks.handlers.action import Action
from src.config import logger


class PrintAction(Action):
    def __init__(self, name: str):
        super().__init__(name=name)

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)  # this is required
        """
        Custom run method. Add your custom logic here.
        """
        data = self.validate_data()  # always get data from webhook by calling this method!
        logger.info(f'Data from webhook:{data}')
