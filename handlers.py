from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext


import keyboards as kb
import middlewares as mw
import database.requests as req

router = Router()

# класс для регистрации пользователей
class Reg(StatesGroup):
    name = State()
    number = State()

# мидлвар который обрабатывает любой известный хендлер
router.message.middleware(mw.InMiddleware())

# мидлвар который обрабатывает любое сообщение
router.message.outer_middleware(mw.OutMiddleware())


# Стартовая команда, возвращает текст с инфой о пользователе, и клавиатуру
@router.message(CommandStart())
async def cmd_start(message: Message):
    await req.set_user(message.from_user.id, message.from_user.full_name)
    await message.answer(f'Привет! \n Твой ID: {message.from_user.id} \n {message.from_user.full_name} \n {message.from_user.language_code}',
                         reply_markup=kb.main_callback)

# команда inline_builder возвращает инлайн клавиатуру
@router.message(Command('inline_builder'))
async def get_i_builder(message: Message):
    await message.answer(f'Привет! \n Выбери ЗН', reply_markup=await kb.inline_zn())

# команда reply_builder возвращает реплай клавиатуру
@router.message(Command('reply_builder'))
async def get_r_builder(message: Message):
    await message.answer(f'Привет! \n Выбери ЗН', reply_markup=await kb.reply_zn())

# команда help
@router.message(Command('help'))
async def get_help(message: Message):
    await message.answer('Это команда /help')

# роутер который ловит конкретную фразу
@router.message(F.text == 'Как дела?')
async def how_are_you(message: Message):
    await message.answer('OK!')

# роутер первого шага регистрации
@router.message(Command('reg'))
async def reg_one(message: Message, state: FSMContext):
    # выставляем состояние fsm что бы отловить ввод имени
    await state.set_state(Reg.name)
    await message.answer('Введите свое имя', reply_markup=ReplyKeyboardRemove())


# роутер второго шага регистрации
@router.message(Reg.name)
async def reg_name(message: Message, state: FSMContext):
    # обновляем стейт только что отловленным именем из текста сообщения
    await state.update_data(name=message.text)
    # обновляем состояние fsm что бы отловить номер телефона
    await state.set_state(Reg.number)
    # запрос номера телефона с помощью клавиатуры
    await message.answer('Введите свой номер телефона', reply_markup=kb.get_user_number)

@router.message(Reg.number)
async def reg_number(message: Message, state: FSMContext):
    if message.text:
        await message.answer(f'Вы ввели номер вручную\n {message.text}')
        await state.update_data(number=message.text)
    else:
        await message.answer(f'Вы прислали контакт')
        await state.update_data(number=message.contact.phone_number)
    # await state.update_data(number=message.contact.phone_number)
    data = await state.get_data()
    # выводим все что ввели
    await message.answer(f'Готово! \n Вы ввели \n {data["number"]} \n {data["name"]}', reply_markup=ReplyKeyboardRemove())
    # обязательная очистка стейта
    await state.clear()

# роутер который ловит колбек
@router.callback_query(F.data == 'catalog')
async def catalog(callback: CallbackQuery):
    await callback.answer('Закрытие ЗН')
    await callback.message.edit_text('Выберете ЗН', reply_markup=await kb.inline_zn())