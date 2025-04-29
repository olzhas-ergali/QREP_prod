from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import aiosmtplib
import smtplib, ssl
from service.API.config import settings


class Mail:
    def __init__(
            self,
            host=settings.mail.MAIL_HOST,
            port=settings.mail.MAIL_PORT,
            username=settings.mail.MAIL_USERNAME,
            password=settings.mail.MAIL_PASSWORD,
            encrypt=settings.mail.MAIL_ENCRYPTION
    ):
        self.__host = host
        self.__port = port
        self.__username = username
        self.__password = password
        self.__encrypt = encrypt
        self.__server = aiosmtplib.SMTP(
            hostname=host,
            port=port,
            start_tls=False,
            use_tls=True,
            username=username,
            password=password
        )

    async def send_message(
            self,
            message: str,
            subject: str,
            to_address: list
    ):
        msg = MIMEMultipart()
        msg.preamble = subject
        msg['Subject'] = subject
        msg['From'] = self.__username
        msg['To'] = ', '.join(to_address)
        msg.attach(MIMEText(message, 'html', 'utf-8'))
        await self.__server.connect()
        await self.__server.send_message(msg)
        await self.__server.quit()
        # self.server.login(self.username, self.password)
        # self.server.send_message(self.username, to_address, message)
