from service.tgbot.lib.SendPlusAPI.base import BaseApi, MethodRequest


class SendPlus(BaseApi):

    def __init__(
            self,
            client_id: str,
            client_secret: str,
            waba_bot_id: str
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.waba_bot_id = waba_bot_id
        super().__init__()

    async def send_template_by_phone(
            self,
            phone: str,
            bot_id: str,
            json: dict = None
    ):
        url = self.url.format(method='contacts/sendTemplateByPhone')
        local = await self.get_local_by_phone(
            phone=phone
        )
        result = await self.request_session(
            method=MethodRequest.post,
            url=url,
            client_id=self.client_id,
            client_secret=self.client_secret,
            json_status=True,
            answer_log=False,
            params={'phone': phone},
            json={
                "bot_id": bot_id,
                "phone": phone,
                "template": json.get(local)
            }
        )

        return result

    async def send_by_phone(
            self,
            phone: str,
            bot_id: str,
            text: str = None,
            texts: dict = None
    ):
        url = self.url.format(method='contacts/sendByPhone')
        local = await self.get_local_by_phone(
            phone=phone
        )
        result = await self.request_session(
            method=MethodRequest.post,
            url=url,
            client_id=self.client_id,
            client_secret=self.client_secret,
            json_status=True,
            answer_log=False,
            #params={'phone': phone},
            json={
                "bot_id": bot_id,
                "phone": phone,
                "message": {
                    "type": "text",
                    "text": {
                        "body": texts.get(local) if texts else text
                    }
                }
            }
        )

        return result

    async def get_local_by_phone(
            self,
            phone: str,
            json: dict = None
    ):
        url = self.url.format(method='contacts/getByPhone')
        result = await self.request_session(
            method=MethodRequest.get,
            url=url,
            client_id=self.client_id,
            client_secret=self.client_secret,
            json_status=True,
            answer_log=False,
            params={'phone': phone, 'bot_id': self.waba_bot_id}
        )

        if result.get('data'):
            return result.get('data').get('variables').get('local')
        return 'rus'

