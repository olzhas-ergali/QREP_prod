from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import ssl
import aiosmtplib
from service.API.config import settings


def _tls_context_insecure():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


class Mail:
    def __init__(
            self,
            host=settings.mail.MAIL_HOST,
            port=settings.mail.MAIL_PORT,
            username=settings.mail.MAIL_USERNAME,
            password=settings.mail.MAIL_PASSWORD,
            encrypt=settings.mail.MAIL_ENCRYPTION,
            tls_insecure=settings.mail.MAIL_TLS_INSECURE,
    ):
        self.__host = host
        self.__port = port
        self.__username = username
        self.__password = password
        self.__encrypt = (encrypt or "ssl").strip().lower()
        if self.__encrypt == "starttls":
            use_tls, start_tls = False, True
        else:
            use_tls, start_tls = True, False
        tls_context = _tls_context_insecure() if tls_insecure else None
        self.__server = aiosmtplib.SMTP(
            hostname=host,
            port=port,
            start_tls=start_tls,
            use_tls=use_tls,
            username=username,
            password=password,
            tls_context=tls_context,
        )

    async def send_message(
            self,
            message: str,
            subject: str,
            to_address: list
    ):
        msg = MIMEMultipart()
        #msg.preamble = str(Header(subject, 'utf-8'))
        msg['Subject'] = str(Header(subject, 'utf-8'))
        msg['From'] = self.__username
        msg['To'] = ', '.join(to_address)
        msg.attach(MIMEText(message, 'html', 'utf-8'))
        await self.__server.connect()
        await self.__server.send_message(msg)
        await self.__server.quit()
        # self.server.login(self.username, self.password)
        # self.server.send_message(self.username, to_address, message)
