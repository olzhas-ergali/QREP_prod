import json
import requests
import logging
from base64 import b64encode


class TYPES:
    POST = 'post'
    GET = 'get'


class REQUESTS:
    BALANCE = "http://91.215.139.187/qr_center_ut/hs/telegram_bot/balance/"
    AUTHORIZATION = "http://91.215.139.187/qr_center_ut/hs/telegram_bot/authorization"
    STOCK = "http://91.215.139.187/qr_center_ut/hs/telegram_bot/stock"
    ACCRUAL = "http://91.215.139.187/qr_center_ut/hs/telegram_bot/accrual"


class OneC:

    @classmethod
    async def get_answer(cls,
                         request: str,
                         type_request: str,
                         obj: object,
                         json_data: dict = None):
        #auth_1c = obj.bot.get('config').get('one_c')
        auth_1c = obj.get('config').one_c
        user_auth = b64encode(bytes(auth_1c.login + ":" + auth_1c.password,
                                    encoding="ascii")).decode("ascii")
        headers = {'Authorization': 'Basic %s' % user_auth}
        logging.info(f"METHOD -> {type_request}\n"
                     f"REQUEST -> {request}\n"
                     f"DATA -> {json_data}")
        if type_request == 'post':
            try:
                headers['Content-Type'] = 'application/json'
                if json_data:
                    resp = requests.post(request, json=json_data, headers=headers)
                    logging.info(f"STATUS CODE -> {resp.status_code}")
                else:
                    logging.info("Данные для post запроса пусты")
            except Exception as ex:
                logging.info(ex)
                return False

        if type_request == 'get':
            try:
                resp = requests.get(request, headers=headers)
                logging.info(f"STATUS CODE -> {resp.status_code}")
            except Exception as ex:
                logging.info(ex)
                return False

        if resp.status_code == 200:
            test_string = resp.text
            return json.loads(test_string)

        return False
