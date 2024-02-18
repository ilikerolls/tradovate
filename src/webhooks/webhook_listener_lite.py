import os.path
import time
import json
import webhook_listener
import ngrok
from src.tradovate.config import logger, CONFIG
from src.constants import SSL_CRT, SSL_KEY
from src.webhooks.events.action import ActionManager


class WHListener:
    def __init__(self, port: int = 8000, auto_start: bool = True):
        """
        Webhook Server Listener
        :param port: Optional: Port number to listen on. Default: 8000
        :param auto_start: Optional: True = Start Listening for Webhooks, False = Must start Manually with start method
        """
        self._wh_server = None
        self._ngrok_listener = None
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
            if len(body_json) > 0:
                logger.info(f"Webhook Data Successfully Received\n{body_json}")
                for action in self.action_man.get_all():
                    action.set_data(data=body_json)
                    action.run()
        except Exception as e:
            logger.error(f"Error Processing Incoming JSON call:\n{e}")

    def start(self):
        """
        Start a Webhook Listener in the background through Python Threading
        NGROK: https://ngrok.github.io/ngrok-python/index.html#full-configuration
        """
        # if os.path.isfile(SSL_CRT) and os.path.isfile(SSL_KEY):
        #    self._wh_server = webhook_listener.Listener(handlers={"POST": self._process_post_request}, port=self.port,
        #                                                sslCert=SSL_CRT, sslPrivKey=SSL_KEY)
        #    logger.info(f"Webhook Listener: SSL Enabled with CRT: {SSL_CRT}, KEY: {SSL_KEY}")
        # else:
        self._wh_server = webhook_listener.Listener(host='127.0.0.1', handlers={"POST": self._process_post_request},
                                                    port=self.port, logger=logger, logScreen=True)
        # logger.warning(f"Webhook Listener: SSL Disabled. Couldn't find SSL files CRT: {SSL_CRT}, KEY: {SSL_KEY}")
        logger.info(f"Started Webhook Listener on {self._wh_server.host}:{self._wh_server.port} and putting it in the "
                    f"background via a Thread...")
        if CONFIG['WEBHOOK']['NGROK']['enabled']:
            self._ngrok_listener = ngrok.forward(f"127.0.0.1:{self.port}",
                                                 authtoken=CONFIG['WEBHOOK']['NGROK']['authtoken'], schemes=["http"],
                                                 proto='http')
            logger.info(f"Started NGROK on {self._ngrok_listener.url()}")
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
