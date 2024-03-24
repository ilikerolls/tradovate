from src.config import logger
from src.utils.general import snake_case, csv_to_list
from src.config import CONFIG_HANDLERS
from importlib import import_module


class TaskManager:
    def __init__(self):
        """
        :param mod_path: Default Module Path to
        """
        self._tasks: dict = {}
        self.man_name: str = str(type(self).__name__)

    def __len__(self) -> int: return len(self._tasks)

    def add(self, name: str):
        """
        Registers action with manager
        :param name: Name of the Task(Action/Alert) ex: print or ninjatrader
        """
        raise NotImplemented

    def _add(self, mod_path: str, name: str) -> bool:
        """
        Import a module & add it to the Manager
        :param mod_path: ex: 'src.webhooks.handlers.actions.print_action'
        :param class_name: Name of Class to Import ex: PrintAction
        :returns True = Successfully added Task to Manager, False = Couldn't add it to the Manager
        """
        class_name = snake_case(name)
        try:  # Get & import Action Object/class
            self._tasks[name] = getattr(import_module(mod_path, class_name), class_name)(name=name)
            logger.info(f'[{self.man_name}] Registering --->\t{mod_path} with class: {class_name}')
            return True
        except Exception as e:
            logger.exception(
                f"***WARNING: NOT Loading Action [{name}]! Make sure {mod_path} "
                f"with Class Name: {class_name}. Exception Details:\n{e}")
        return False

    def get_all_dict(self) -> dict:
        """
        Gets all actions from manager
        :return: dict of {'action_name': action_object}
        """
        return self._tasks

    def get_all_list(self) -> list:
        """
        :return: Return a list of Action Objects as opposed to a dict of {'action_name': action_object}
        """
        return list(self._tasks.values())

    def get(self, name: str):
        """
        Gets action from manager that matches given name
        :param name: name of task/action/alert
        :return: Manager Task Object
        """
        try:
            return self._tasks[name]
        except KeyError:
            logger.error(f"{self.man_name}: [{name}] not loaded in Action Manager: {self._tasks.keys()}")
        return None


class ActionManager(TaskManager):
    def add(self, name: str):
        """
        Registers Action with Manager
        :param name: Name of the Action ex: print or tradovate
        """
        self._add(mod_path=f'src.webhooks.handlers.actions.{name}', name=name)


class AlertManager(TaskManager):
    def add(self, name: str):
        """
        Registers Action with Manager
        :param name: Name of the Action ex: print or tradovate
        """
        self._add(mod_path=f'src.webhooks.handlers.alerts.{name}', name=name)


class Action:
    NAME = None

    def __init__(self, name: str):
        """
        :param name: Name of Action File without .py suffix ex: print_action, ninjatrader_action
        """
        self.NAME = str(type(self).__name__)
        self.name: str = name
        self._alerts: dict = {}
        self.data = None
        self.conf: dict | None = None
        try:
            self.conf = CONFIG_HANDLERS[name.lower()]
            logger.debug(f"[{self.NAME}] - Loaded Configuration")
            if 'ALERTS' in self.conf.keys():
                self._alerts = self.conf['ALERTS']
        except KeyError:
            logger.debug(f"Warning: [{self.NAME}] - No Configuration to load.")

    def __str__(self): return self.NAME

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
