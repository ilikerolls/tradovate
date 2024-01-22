from src.webhooks.events.action import Action

"""Action name should match action file name for Example: file name: template_action_class.py,
Class Name: TemplateActionClass"""


class TemplateActionClass(Action):
    def __init__(self):
        super().__init__()

    def run(self, *args, **kwargs):
        """
        Custom run method. Add your custom logic here.
        """
        super().run(*args, **kwargs)
