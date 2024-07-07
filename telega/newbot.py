import os

from aiogram.types.callback_query import CallbackQuery
from dotenv import load_dotenv

load_dotenv()
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

from aiogram_dialog import (
    Dialog, DialogManager, setup_dialogs, StartMode, Window,
)

from aiogram.types import CallbackQuery

from aiogram_dialog import Window, Dialog, DialogManager
from aiogram_dialog.widgets.kbd import Button, Back
from aiogram_dialog.widgets.text import Const, Format


class MySG(StatesGroup):
    main = State()


main_window = Window(
    Const("Hello, unknown person"),
    Button(Const("Useless button"), id="nothing"),
    state=MySG.main,
)
dialog = Dialog(main_window)

TOKEN_BOT = os.getenv('TOKEN_BOT')

storage = MemoryStorage()
bot = Bot(token=TOKEN_BOT)
dp = Dispatcher(storage=storage)
dp.include_router(dialog)
setup_dialogs(dp)


class MySG(StatesGroup):
    window1 = State()
    window2 = State()
    main = State()

async def window1_get_data(**kwargs):
    return {
        "something": "data from Window1 getter",
    }


async def window2_get_data(**kwargs):
    return {
        "something": "data from Window2 getter",
    }


async def dialog_get_data(**kwargs):
    return {
        "name": "Tishka17",
    }


@dp.message(Command("start"))
async def start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MySG.main, mode=StartMode.RESET_STACK)


async def button1_clicked(callback: CallbackQuery, button: Button, manager: DialogManager):
    """ Add data to `dialog_data` and switch to the next window of current dialog """
    manager.dialog_data['user_input'] = 'some data from user, stored in `dialog_data`'
    await manager.next()


dialog = Dialog(
    Window(
        Format("Hello, {name}!"),
        Format("Something: {something}"),
        Button(Const("Next window"), id="button1", on_click=button1_clicked),
        state=MySG.window1,
        getter=window1_get_data,  # here we specify data getter for window1
    ),
    Window(
        Format("Hello, {name}!"),
        Format("Something: {something}"),
        Format("User input: {dialog_data[user_input]}"),
        Back(text=Const("Back")),
        state=MySG.window2,
        getter=window2_get_data,  # here we specify data getter for window2
    ),
    getter=dialog_get_data  # here we specify data getter for dialog
)


async def button1_clicked(callback: CallbackQuery, button: Button, manager: DialogManager):
    dialog_data = manager.dialog_data
    event = manager.event
    middleware_data = manager.middleware_data
    start_data = manager.start_data


if __name__ == '__main__':
    dp.run_polling(bot, skip_updates=True)
