from src.webhooks.handlers.action import Action

"""Action name should match action file name for Example: file name: template_action_class.py,
Class Name: TemplateActionClass"""


class TemplateActionClass(Action):
    """Template for Creating New Actions"""
    def __init__(self, action_name: str):
        """
        :param action_name: Name given to Action by Action Manager
        """
        super().__init__(action_name=action_name)

    def run(self, *args, **kwargs):
        """
        Custom run method. Add your custom logic here.
        """
        super().run(*args, **kwargs)
