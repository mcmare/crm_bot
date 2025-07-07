from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, Message)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from database.requests import get_order

# переменная содержит Reply клавиатуру, список в списке, в одном списке одна строка клавиш
# resize_keyboard изменяет размер клавиш на низкие
# input_field_placeholder пишет текст в строке ввода, типа подсказка

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='/inline_builder')],
    [KeyboardButton(text='/reply_builder'), KeyboardButton(text='Контакты')]
],
    resize_keyboard=True,
    input_field_placeholder='Выберете пункт меню')

main_callback = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Список ЗН', callback_data='catalog')],
    [InlineKeyboardButton(text='Корзина', callback_data='basket'), InlineKeyboardButton(text='Контакты', callback_data='contacts')],
])

#клавиатура запроса номера телефона в виде контакта
get_user_number = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Ввести номер телефона', request_contact=True)]
],resize_keyboard=True)

# переменная содержит Inline клавиатуру, список в списке, в одном списке одна строка клавиш
# каждая клавиша, помимо text, должна содержать еще что-то, например url для перехода на страницу,
# или web_app для открытия веб приложения

settings = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Закрыть ЗН', web_app=WebAppInfo(url=f'https://google.com'))]
])




# Асинхронная функция генерации клавиатуры из списка, в данном случае zn,
# keyboard.adjust(4) указывает сколько колонок
# клавиатура принимает только строки
async def reply_zn():
    keyboard = ReplyKeyboardBuilder()
    zn = await get_order()
    for i in zn:
        keyboard.add(KeyboardButton(text=str(i)))
    return keyboard.adjust(4).as_markup()

async def inline_zn(tg_id):
    tg_id = tg_id
    zn = await get_order(tg_id)
    keyboard = InlineKeyboardBuilder()
    for i in zn:
        keyboard.add(InlineKeyboardButton(text=str(i.n_order_work), callback_data=f'ZN_{i.n_order_work}'))
    return keyboard.adjust(4).as_markup()

