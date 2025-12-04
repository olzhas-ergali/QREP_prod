# service/tgbot/filters/admin.py
import typing
from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.handler import ctx_data
from service.API.infrastructure.database.models import User

class AdminFilter(BoundFilter):
    key = 'is_admin'

    def __init__(self, is_admin: typing.Optional[bool] = None):
        self.is_admin = is_admin

    async def check(self, *args):
        data = ctx_data.get()
        user: User = data.get('user')
        
        is_admin_flag = False
        if isinstance(user, User) and user.profile:
            is_admin_flag = user.profile.is_admin

        if self.is_admin is None:
            return True
        
        return self.is_admin == is_admin_flag