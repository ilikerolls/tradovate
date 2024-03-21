import time
import json
import webhook_listener
import ngrok
from src.config import logger, CONFIG
from src.webhooks.handlers.action import ActionManager


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
        for action_name in CONFIG['WEBHOOK']['handlers']:
            self.action_man.add(name=action_name)
        if auto_start:
            self.start()

    def __del__(self):
        self.stop()

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
                for [a_name, action_obj] in self.action_man.get_all_dict().items():
                    try:
                        action_obj.set_data(data=body_json)
                        action_obj.run()
                    except Exception as e:
                        logger.warning(f"Failed to run action: {a_name}. Error:\n{e}")
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
            logger.info(f"Started NGROK - Add this address: {self._ngrok_listener.url()} to your TradingView Alert under Webhook URL in the Settings tab")
        logger.info("Add {{strategy.order.alert_message}} to your TradingView Alert Message")
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
