from src.webhooks.events.action import Action


class TemplateActionClass(Action):
    def __init__(self):
        super().__init__()

    def run(self, *args, **kwargs):
        """
        Custom run method. Add your custom logic here.
        """
        super().run(*args, **kwargs)