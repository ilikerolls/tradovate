from src.webhooks.handlers.action import Action

"""Action name should match action file name for Example: file name: template_action_class.py,
Class Name: TemplateActionClass"""


class TemplateAction(Action):
    """Template for Creating New Actions"""

    def __init__(self, name: str):
        """
        :param action_name: Name given to Action by Action Manager
        """
        super().__init__(name=name)

    def run(self, *args, **kwargs):
        """
        Custom run method. Add your custom logic here.
        """
        super().run(*args, **kwargs)


if __name__ == "__main__":
    test = TemplateAction()
    print(f"Action Name: {str(test)}")
