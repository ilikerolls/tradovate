from src.config import logger
from src.utils.general import snake_case
from src.config import CONFIG_HANDLERS
from importlib import import_module


class ActionManager:
    def __init__(self):
        self._actions = {}

    def add_action(self, name: str):
        """
        Registers action with manager
        :param name: Name of the Action ex: print or tradovate
        """
        class_name = snake_case(f'{name}_action')
        logger.info(f'Registering action --->\tsrc.webhooks.handlers.actions.{name}_action with class: {class_name}')
        try:  # Get & import Action Object/class
            action = getattr(import_module(f'src.webhooks.handlers.actions.{name}_action', class_name), class_name)(action_name=name)
            self._actions[name] = action
        except Exception as e:
            logger.exception(
                f"***WARNING: NOT Loading Action [{name}]! Make sure src.webhooks.handlers.actions.{name}_action.py exits "
                f"with Class Name: {class_name}. Exception Details:\n{e}")

    def get_all_dict(self) -> dict:
        """
        Gets all actions from manager
        :return: dict of {'action_name': action_object}
        """
        return self._actions

    def get_all_list(self) -> list:
        """
        :return: Return a list of Action Objects as opposed to a dict of {'action_name': action_object}
        """
        return list(self._actions.values())

    def get(self, action_name: str):
        """
        Gets action from manager that matches given name
        :param action_name: name of action
        :return: Action Object or None if it's not loaded in the Action Manager
        """
        try:
            return self._actions[action_name]
        except KeyError:
            logger.error(f"Action: [{action_name}] not loaded in Action Manager: {self._actions.keys()}")
        return None


class Action:
    # action_man = ActionManager()

    def __init__(self, action_name: str):
        self.class_name = str(type(self).__name__)
        self.action_name: str = action_name
        # self.logs = []
        self.data = None
        self.conf: dict or None = None
        try:
            self.conf = CONFIG_HANDLERS[self.action_name]
            logger.debug(f"Action: [{self.action_name}] - Loaded Configuration\n{self.conf}")
        except KeyError:
            logger.debug(f"Action [{self.action_name}] - No Configuration to load.")

    def __str__(self):
        return f'{self.class_name}'

    # def get_logs(self):
    #     """
    #     Gets run logs in descending order
    #     :return: list
    #     """
    #     return self.logs

    def set_data(self, data: dict):
        """Sets data for action"""
        self.data = data

    def validate_data(self):
        """Ensures data is valid"""
        if not self.data:
            raise ValueError('No data provided to action')
        return self.data

    def run(self, *args, **kwargs):
        """
        Runs, logs action
        """
        logger.info(f'ACTION TRIGGERED --->\t{str(self)}')
        return self.validate_data()
        # self.logs.append(ActionLogEvent('INFO', 'action run'))
        # log_event = LogEvent(self.name, 'action_run', datetime.datetime.now(), f'{self.name} triggered')
        # log_event.write()
