import json
import logging
import typing

import aiohttp

from service.tgbot import config

SENDPULSE_TIMEOUT_TOTAL = 30
SENDPULSE_TIMEOUT_CONNECT = 10


class MethodRequest:
    post = 'POST'
    put = 'PUT'
    get = 'GET'
    delete = 'DELETE'
    patch = 'PATCH'


def to_format(
        data
) -> str:
    if data is None:
        return ""
    return data


class BaseApi:

    def __init__(
            self
    ):
        self.production_url = 'https://api.sendpulse.com/whatsapp/{method}'

    @property
    def url(self) -> str:
        return self.production_url

    @classmethod
    async def request_session(
            cls,
            method: MethodRequest.get,
            url: str,
            client_id: str,
            client_secret: str,
            json_status: bool = True,
            answer_log: bool = False,
            **kwargs
    ):

        logging.info(
            f"METHOD {method}\nURL - {url}\n"
            f"dict - > {kwargs}"
        )

        timeout = aiohttp.ClientTimeout(total=SENDPULSE_TIMEOUT_TOTAL, connect=SENDPULSE_TIMEOUT_CONNECT)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            token_url = 'https://api.sendpulse.com/oauth/access_token'
            response = await session.request(
                method=MethodRequest.post,
                url=token_url,
                data={"grant_type": "client_credentials"},
                auth=aiohttp.BasicAuth(client_id, client_secret)
            )
            logging.info(response)
            data = await response.read()
            data = json.loads(data)
            print(data)
            response = await session.request(
                method=method,
                url=url,
                headers={'Authorization': 'Bearer {}'.format(data.get('access_token'))},
                timeout=timeout,
                **kwargs
            )
            print(response.status)
            if response.status == 400:
                logging.info(await response.text())
                logging.info("STATUS CODE -> 400")
                return {
                    "status_code": 400
                }

            try:
                if json_status:
                    logging.info(await response.text())
                    data = await response.read()
                    data = json.loads(data)
                    return data
            except Exception as e:
                logging.exception(e)
            finally:
                if answer_log:
                    logging.info(
                        f'ANSWER: {await response.text()}'
                    )

            return response
