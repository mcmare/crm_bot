from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any, Awaitable
from datetime import datetime

def t():
    t = datetime.now()
    t = t.strftime("%H:%M:%S:%f")
    return t


class InMiddleware(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any]) -> Any:
        print(f'{t()} In Действия до обработчика')
        result = await handler(event, data)
        print(f'{t()} In Действия после обработчика')
        return result


class OutMiddleware(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any]) -> Any:
        print(f'{t()} Out Действия до обработчика')
        result = await handler(event, data)
        print(f'{t()} Out Действия после обработчика')
        return result
