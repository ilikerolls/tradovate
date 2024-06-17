import smtplib
from email.message import EmailMessage

from src.config import logger


class SendEmail:
    """Send an Email"""
    NAME = None

    def __init__(self, login: str, passwd: str, sender_email: str = None, recipients: list | str = None,
                 host: str = 'smtp-mail.outlook.com', port: int = 587, ssl: bool = False, tls: bool = True):
        """
        :param login: Login Name for the Email Account
        :param passwd: Password to log into Email Server
        :param sender_email: Optional: Sender's Email Address(default same as login)
        :param recipients: Optional: List or comma delimited string of Email Addresses to send to ex: ['joe.blow@gmail.com', 'camelToe@hotmail.com']
        :param host: Host of Email Account tp connect to example: 'smtp.gmail.com'
        :param port: Port of Email Server to connect to
        :param ssl: True = Use SSL, False = Do NOT Use SSL
        :param tls: True = Use TLS, False = Do Not Use TLS
        """
        self.NAME = self.__class__.__name__
        self.host = host
        self.port = port
        self.login = login
        self.passwd = passwd
        self.sender_email = login if sender_email is None else sender_email
        self.recipients = ', '.join(recipients) if isinstance(recipients, list) else recipients
        self.use_ssl = ssl
        self.use_tls = tls

    def run(self, subject: str, msg: str, recipients: list | str = None):
        try:
            self.send_email(subject=subject, body=msg, recipients=recipients)
        except Exception as e:
            logger.exception(f"ERROR: [{self.NAME}] - Failed to run Alert.\nRecipients: {recipients or self.recipients}\nSubject: "
                             f"{subject}\nMessage: {msg}\nError:\n{e}")

    def send_email(self, subject: str, body: str, recipients: list | str = None) -> str:
        """
        Send an Email
        :param subject: Subject of the Email
        :param body: Body of the Email
        :param recipients: Optional: List or comma delimited string of Email Addresses to send to ex: ['joe.blow@gmail.com', 'camelToe@hotmail.com']
        :returns Email Messsage sent in String format
        """
        to_list = self.recipients
        if recipients is not None:  # to_list must be a comma delimited list
            to_list = ', '.join(recipients) if isinstance(recipients, list) else recipients
        msg = EmailMessage()
        msg['From'] = self.sender_email
        msg['To'] = to_list
        msg['Subject'] = subject
        msg.set_content(body)

        if not self.use_ssl:
            with smtplib.SMTP(host=self.host, port=self.port) as smtp_server:
                self._send_email(smtp_server=smtp_server, msg=msg)
        else:
            with smtplib.SMTP_SSL(host=self.host, port=self.port) as smtp_server:
                self._send_email(smtp_server=smtp_server, msg=msg)
        return body

    def _send_email(self, smtp_server: smtplib.SMTP | smtplib.SMTP_SSL, msg: EmailMessage):
        smtp_server.ehlo()
        if self.use_tls:
            smtp_server.starttls()
        smtp_server.login(self.login, self.passwd)
        smtp_server.send_message(msg=msg)