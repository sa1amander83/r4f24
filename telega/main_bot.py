import asyncio
import logging
import os
import sys
from datetime import datetime

import django
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage

from aiogram.utils.formatting import Text

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "r4f24.settings")
django.setup()

from aiogram import Bot, Dispatcher, types, F
from django.conf import settings
from django.contrib.auth import authenticate
from django.db.models import Sum

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
import r4f24
from core.models import User
from profiles.models import RunnerDay, Photo, Teams
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

# from aiogram.contrib.middlewares.logging import LoggingMiddleware


storage = MemoryStorage()
logging.basicConfig(level=logging.INFO)
bot = Bot(os.getenv('TOKEN_BOT'))
dp = Dispatcher()

user_sessions = {}


class ProfileStateGroup(StatesGroup):
    username = State()
    password = State()
    # age = State()
    # description = State()


# def get_kb() -> ReplyKeyboardMarkup:
#     kb = [
#         [types.KeyboardButton(text='Вход')],
#         [types.KeyboardButton(text='Выход')],
#         [types.KeyboardButton(text='Пробежка')],
#         [types.KeyboardButton(text='Моя группа')],
#         [types.KeyboardButton(text='Статистика')],
#         [types.KeyboardButton(text='Чемпионат')],
#         [types.KeyboardButton(text='Команды')],
#         [types.KeyboardButton(text='Группы')],
#
#     ]
#     keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, )
#
#     return keyboard


@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    kb = [
        [types.KeyboardButton(text='Вход')],
        [types.KeyboardButton(text='Выход')],
        [types.KeyboardButton(text='Пробежка')],
        [types.KeyboardButton(text='Моя группа')],
        [types.KeyboardButton(text='Статистика')],
        [types.KeyboardButton(text='Чемпионат')],
        [types.KeyboardButton(text='Команды')],
        [types.KeyboardButton(text='Группы')],

    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, )

    await message.reply("Hi! Use the menu below to interact with the bot.", reply_markup=get_kb())


@dp.message()
async def command_create(message: types.Message) -> None:
    await message.answer(
        text=F"Давай создадим наш профиль!Отправь мне свою фотографию -> 📷",
        reply_markup=send_welcome())
    await message.answer(text='Теперь отправь свое имя!')
    await ProfileStateGroup.next()


# class Form(StatesGroup):
#     waiting_for_username = State()
#     waiting_for_password = State()
#
#
# @dp.message(commands='start', state='*')
# async def start_login(message: types.Message):
#     await Form.waiting_for_username.set()
#     await message.answer("Please enter your username:")
#
#
# @dp.message(state=Form.waiting_for_username)
# async def process_username(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['username'] = message.text
#     await Form.next()
#     await message.answer("Please enter your password:")
#
#
# @dp.message(state=Form.waiting_for_password)
# async def process_password(message: types.Message, state: FSMContext):
#     username = (await state.get_data())['username']
#     password = message.text
#
#     user = authenticate(username=username, password=password)
#     if user is not None:
#         await message.answer("You are successfully authenticated!")
#     else:
#         await message.answer("Invalid username or password.")
#
#     await state.finish()
#


@dp.message(F.text.lower() == "вход")
async def login_command(message: types.Message):
    await process_login(message)

    # elif 'login' in message.text:
    #     login_user(message)


def process_login(message):
    bot.send_message(message.chat.id, 'Введите логин и пароль')
    try:
        login = message.text.split()[1]
        password = message.text.split()[2]
        user = authenticate(username=login, password=password)
        if user is not None:
            user_sessions[message.chat.id] = user.id
            bot.send_message(message.chat.id, 'Вы авторизованы!')
        else:
            bot.send_message(message.chat.id, 'Неправильный логин или пароль')
    except ValueError:
        bot.send_message(message.chat.id,
                         'Введите логин и пароль в формате: /login логин пароль')


# @dp.message(Text(equals="Login:", prefixes=["/"]))
# async def login_handler(message):
#     await process_login(message)


@dp.message(F.text.lower() == "/login")
async def login_user(message):
    try:
        _, username, password = message.text.split()
        user = authenticate(username=username, password=password)
        if user is not None:
            user_sessions[message.chat.id] = user.id
            await bot.send_message(message.chat.id, 'Вы авторизованы!')
        else:
            await bot.send_message(message.chat.id, 'Неправильный логин или пароль')
    except ValueError:
        await bot.send_message(message.chat.id,
                               'Введите логин и пароль в формате: /login логин пароль')


@dp.message(state='*')
#
# @bot.message_handler(lambda message: message.text == "Logout")
# async def logout_command(message: types.Message):
#     user_sessions.pop(message.chat.id, None)
#     await bot.send_message(message.chat.id, 'Logged out successfully!')
#
#
# @bot.message_handler(lambda message: message.text == "Input Run")
# async def input_run(message: types.Message):
#     await bot.send_message(message.chat.id,
#                            'Please enter your run details in the format: /input_run distance time average_temp')
#
#
# #
# @bot.message_handler(commands=['input_run'])
# async def save_run(message: types.Message):
#     try:
#         _, distance, time, average_temp = message.text.split()
#         user_id = user_sessions.get(message.chat.id)
#         if user_id:
#             user = await User.objects.get(id=user_id)
#             runner_day = await RunnerDay.objects.create(
#                 runner=user,
#                 day_select=datetime.now().day,
#                 day_distance=distance,
#                 day_time=time,
#                 day_average_temp=average_temp
#             )
#             await bot.send_message(message.chat.id, 'Run details saved successfully! Please upload images of your run.')
#             user_sessions[message.chat.id] = {'runner_day_id': runner_day.id}
#         else:
#             await bot.send_message(message.chat.id, 'You need to log in first.')
#     except ValueError:
#         await bot.send_message(message.chat.id,
#                                'Please enter your run details in the format: /input_run distance time average_temp')
#
#
# @bot.message_handler(content_types=['photo'])
# async def handle_photo(message: types.Message):
#     user_session = user_sessions.get(message.chat.id)
#     if user_session and 'runner_day_id' in user_session:
#         runner_day_id = user_session['runner_day_id']
#         runner_day = await RunnerDay.objects.get(id=runner_day_id)
#         file_info = await bot.get_file(message.photo[-1].file_id)
#         downloaded_file = await bot.download_file(file_info.file_path)
#
#         # Save the file to the file system
#         file_path = os.path.join(settings.MEDIA_ROOT, 'runs', file_info.file_path)
#         os.makedirs(os.path.dirname(file_path), exist_ok=True)
#         with open(file_path, 'wb') as new_file:
#             new_file.write(downloaded_file)
#
#         # Create a record in the Photo model
#         photo = await Photo.objects.create(
#             runner=runner_day.runner,
#             day_select=runner_day.day_select,
#             number_of_run=runner_day.number_of_run,
#             photo=os.path.join('runs', file_info.file_path)
#         )
#         await bot.send_message(message.chat.id, 'Image uploaded successfully!')
#     else:
#         await bot.send_message(message.chat.id, 'You need to log in and input run details first.')
#
#
# @bot.message_handler(lambda message: message.text == "My Group")
# async def my_group(message: types.Message):
#     user_id = user_sessions.get(message.chat.id)
#     if user_id:
#         user = await User.objects.get(id=user_id)
#         group = user.runner_team
#         if group:
#             members = await User.objects.filter(runner_team=group)
#             member_list = '\n'.join([member.username for member in members])
#             await bot.send_message(message.chat.id, f'Your group: {group.team_name}\nMembers:\n{member_list}')
#         else:
#             await bot.send_message(message.chat.id, 'You are not in any group.')
#     else:
#         await bot.send_message(message.chat.id, 'You need to log in first.')
#
#
# @bot.message_handler(lambda message: message.text == "Total Statistic")
# async def total_statistic(message: types.Message):
#     total_distance = await RunnerDay.objects.aggregate(Sum('day_distance'))['day_distance__sum']
#     total_time = await RunnerDay.objects.aggregate(Sum('day_time'))['day_time__sum']
#     await bot.send_message(message.chat.id, f'Total Distance: {total_distance}\nTotal Time: {total_time}')
#
#
# @bot.message_handler(lambda message: message.text == "All Groups")
# async def all_groups(message: types.Message):
#     groups = await Teams.objects.all()
#     group_list = '\n'.join([group.team_name for group in groups])
#     await bot.send_message(message.chat.id, f'All Groups:\n{group_list}')
#

# async def on_startup(dp):
#     await bot.set_webhook('http://zabeg.su/webhook/')
#
#
# async def on_shutdown(dp):
#     await bot.delete_webhook()

# async def main():
#     await bot.polling(non_stop=True)

async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=os.getenv('TOKEN_BOT'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
# if __name__ == '__main__':
#     asyncio.run(bot.infinity_polling(logger_level=settings.LOG_LEVEL, allowed_updates=util.update_types))
#     # from aiogram import executor
#
#

# from django.core.management import execute_from_command_line
#
# execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])
# executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown,non_stop= True)
