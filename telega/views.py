# telegram_bot/views.py
import os
from datetime import datetime

from django.contrib.auth import authenticate
from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings
import telebot

from core.models import Teams, User, Group
from profiles.models import RunnerDay, Photo

bot = telebot.TeleBot(os.getenv('TOKEN_BOT'))


class TelegramBotView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        json_str = request.body.decode('UTF-8')
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return JsonResponse({'status': 'ok'})


# Define command handlers
user_sessions = {}


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = telebot.types.KeyboardButton('Вход')
    itembtn2 = telebot.types.KeyboardButton('Выход')
    itembtn3 = telebot.types.KeyboardButton('Ввести пробежку')
    itembtn4 = telebot.types.KeyboardButton('Моя группа')
    itembtn5 = telebot.types.KeyboardButton('Статистика')
    itembtn6 = telebot.types.KeyboardButton('Группы')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6)
    bot.send_message(message.chat.id, "Используйте команды бота", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Вход")
def login_command(message):
    bot.send_message(message.chat.id, 'Введите логин и пароль в формате: /login логин пароль')


@bot.message_handler(commands=['login'])
def login_user(message):
    try:
        _, username, password = message.text.split()
        user = authenticate(username=username, password=password)
        if user is not None:
            user_sessions[message.chat.id] = user.id
            bot.send_message(message.chat.id, 'Вы авторизованы!')
        else:
            bot.send_message(message.chat.id, 'Неправильный логин или пароль')
    except ValueError:
        bot.send_message(message.chat.id,
                         'Введите логин и пароль в формате: /login логин пароль')


@bot.message_handler(func=lambda message: message.text == "logout")
def logout_command(message):
    user_sessions.pop(message.chat.id, None)
    bot.send_message(message.chat.id, 'Вы вышли')


@bot.message_handler(func=lambda message: message.text == "Введите пробежку")
def input_run(message):
    bot.send_message(message.chat.id,
                     'Введите данные пробежки через команд /run дистанция время пробежки средний темп')


@bot.message_handler(commands=['run'])
def save_run(message):
    try:
        _, distance, time, average_temp = message.text.split()
        user_id = user_sessions.get(message.chat.id)
        if user_id:
            user = User.objects.get(id=user_id)
            runner_day = RunnerDay.objects.create(
                runner=user,
                day_select=datetime.now().day,
                day_distance=distance,
                day_time=time,
                day_average_temp=average_temp
            )
            bot.send_message(message.chat.id, 'Данные о пробежке внесены, добавьте скриншоты или фотографии пробежки')
            user_sessions[message.chat.id] = {'runner_day_id': runner_day.id}
        else:
            bot.send_message(message.chat.id, 'Сначала авторизируйтесь')
    except ValueError:
        bot.send_message(message.chat.id,
                         'Введите данные пробежки через команд /run дистанция время пробежки средний темп')


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_session = user_sessions.get(message.chat.id)
    if user_session and 'runner_day_id' in user_session:
        runner_day_id = user_session['runner_day_id']
        runner_day = RunnerDay.objects.get(id=runner_day_id)
        file_info = bot.get_file(message.photo[-1].file_id)
        file_name = file_info.file_path.split('/')[1]
        team = str(runner_day.runner)[:3]
        user = str(runner_day.runner)
        day = str(datetime.now().day)
        num_of_run = str(runner_day.number_of_run)
        downloaded_file = bot.download_file(file_info.file_path)

        # file_path = os.path.join(settings.MEDIA_ROOT, 'day_of_month', team, user, day, num_of_run, file_name)
        file_path = f'/day_of_month/{team}/{user}/{day}/{num_of_run}/{file_name}'
        # os.makedirs(os.path.dirname(file_path),exist_ok=True)
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        photo= Photo.objects.update_or_create(runner=runner_day.runner,
                                 number_of_run=runner_day.number_of_run,
                                 day_select=runner_day.day_select,
                                 photo=file_path)
        # runner_day.photo_set.create(photo=f'runs/{file_info.file_path}')

        # Photo.objects.bulk_create(runner_id=runner_day.runner,
        #                      number_of_run=runner_day.number_of_run,
        #                      day_select=runner_day.day_select,
        #                      photo=downloaded_file)

        bot.send_message(message.chat.id, 'Image uploaded successfully!')
    else:
        bot.send_message(message.chat.id, 'You need to log in and input run details first.')


@bot.message_handler(func=lambda message: message.text == "My Group")
def my_group(message):
    user_id = user_sessions.get(message.chat.id)
    if user_id:
        user = User.objects.get(id=user_id)
        group = user.runner_team
        if group:
            members = User.objects.filter(runner_team=group)
            member_list = '\n'.join([member.username for member in members])
            bot.send_message(message.chat.id, f'Your group: {group.team_name}\nMembers:\n{member_list}')
        else:
            bot.send_message(message.chat.id, 'You are not in any group.')
    else:
        bot.send_message(message.chat.id, 'You need to log in first.')


@bot.message_handler(func=lambda message: message.text == "Total Statistic")
def total_statistic(message):
    total_distance = RunnerDay.objects.aggregate(Sum('day_distance'))['day_distance__sum']
    total_time = RunnerDay.objects.aggregate(Sum('day_time'))['day_time__sum']
    bot.send_message(message.chat.id, f'Total Distance: {total_distance}\nTotal Time: {total_time}')


@bot.message_handler(func=lambda message: message.text == "All Groups")
def all_groups(message):
    groups = Group.objects.all()
    group_list = '\n'.join([group.group_title for group in groups])
    bot.send_message(message.chat.id, f'All Groups:\n{group_list}')
