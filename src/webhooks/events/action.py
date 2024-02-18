from src.tradovate.config import logger
from src.utils.general import snake_case
from importlib import import_module


class ActionManager:
    def __init__(self):
        self._actions = []

    def add_action(self, name: str):
        """
        Registers action with manager
        :param name: Name of the Action File ex: print_action
        """
        snake_case_name = snake_case(name)
        logger.info(f'Registering action --->\tsrc.webhooks.events.custom.{name} with class: {snake_case_name}')
        try:  # Get & import Action Object/class
            action = getattr(import_module(f'src.webhooks.events.custom.{name}', snake_case_name), snake_case_name)()
            self._actions.append(action)
        except Exception as e:
            logger.exception(
                f"***WARNING: NOT Loading Action {name}! Couldn't load action from: src.webhooks.events.custom.{name} "
                f"with Class Name: {snake_case_name}. Error:\n{e}")

    def get_all(self):
        """
        Gets all actions from manager
        :return: list of Action()
        """
        return self._actions

    def get(self, action_name: str):
        """
        Gets action from manager that matches given name
        :param action_name: name of action
        :return: Action()
        """
        for action in self._actions:
            if action.name == action_name:
                return action
        raise ValueError(f'Cannot find action with name {action_name}')


class Action:
    # action_man = ActionManager()

    def __init__(self):
        self.name = str(type(self).__name__)
        # self.logs = []
        self.data = None

    def __str__(self):
        return f'{self.name}'

    # def get_logs(self):
    #     """
    #     Gets run logs in descending order
    #     :return: list
    #     """
    #     return self.logs

    #    def register(self):
    #        """ Registers action with manager """
    #        self.action_man._actions.append(self)
    #        logger.info(f'ACTION REGISTERED --->\t{str(self)}')

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
