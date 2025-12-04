# service/tgbot/filters/auth.py
from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.handler import ctx_data
from service.API.infrastructure.database.models import User

class AuthFilter(BoundFilter):
    key = 'is_auth'

    def __init__(self, is_auth):
        self.is_auth = is_auth

    async def check(self, *args) -> bool:
        data = ctx_data.get()
        user: User = data.get('user')
        
        is_active = False
        if isinstance(user, User) and user.profile:
            is_active = user.profile.is_active

        if self.is_auth:
            return is_active
        else:
            return not is_active