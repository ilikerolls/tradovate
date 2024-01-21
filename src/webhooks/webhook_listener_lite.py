import time
import json
import webhook_listener
from src.tradovate.config import logger, CONFIG
from src.webhooks.events.action import ActionManager


class WHListener:
    def __init__(self, port: int = 8000, auto_start: bool = True):
        """
        Webhook Server Listener
        :param port: Optional: Port number to listen on. Default: 8000
        :param auto_start: Optional: True = Start Listening for Webhooks, False = Must start Manually with start method
        """
        self._wh_server = None
        self.port = port
        # Register Actions to be taken On Successful Webhook
        self.action_man = ActionManager()
        for action in CONFIG['WEBHOOK']['actions']:
            self.action_man.add_action(name=action)
        if auto_start:
            self.start()

    def _process_post_request(self, request, *args, **kwargs):
        """
        Process a Webhook Request
        :param request: cherrypy object
        :param args: If any extra arguments are passed?
        :param kwargs: If any extra keyword arguments are passed?
        :return:
        """
        try:
            body = request.body.read(int(request.headers['Content-Length']))
            body_json = json.loads(body.decode('utf-8'))
            logger.info(f"Webhook Data Successfully Received\n{body_json}")
            for action in self.action_man.get_all():
                action.set_data(data=body_json)
                action.run()
            return "Sent alert", 200
        except Exception as e:
            logger.error("[X]", "Error:\n>", e)
            return "Error", 400

    def start(self):
        """
        Start a Webhook Listener in the background through Python Threading
        """
        logger.info("Starting Webhook Listener and putting it in the background via a Thread...")
        self._wh_server = webhook_listener.Listener(handlers={"POST": self._process_post_request}, port=self.port)
        self._wh_server.start()

    def stop(self):
        """
        Gracefully Stop the Webhook Server from listening
        """
        if self._wh_server is not None:
            logger.info("Stopping Webhook Listener...")
            self._wh_server.stop()


if __name__ == "__main__":
    """ Example Usage """
    wh_server = WHListener()
    wh_server.start()
    while True:
        print("Still alive...")
        time.sleep(300)
