import csv

from django.contrib import admin, messages

# Register your models here.
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, path
from django.utils.safestring import mark_safe

from core.models import User
from profiles.models import RunnerDay, Statistic
from r4f24.forms import UserImportForm


class RunnerAdmin(admin.ModelAdmin):
    # resource_class = TeamsAdmin
    # def пробег_за_день(self, username, day_distance=None):
    #     result = RunnerDay.objects.filter(user__user__username=username).filter(
    #         user__runnerday__day_distance=day_distance)
    #
    #     return result
    #
    # def дистанция_за_день(self, username):
    #     result = RunnerDay.objects.filter(user__user__username=username)
    #     return result
    #
    # def время_пробега(self, username):
    #     result = RunnerDay.objects.filter(user__user__username=username)
    #     return result
    #
    # def средний_темп(self, username):
    #     result = RunnerDay.objects.filter(user__user__username=username)
    #     return result

    # fields = ('пробег_за_день', 'дистанция_за_день', 'время_пробега', 'средний_темп',)
    search_fields = ('username', 'runner_team__team', 'runner_age', 'runner_category', 'runner_gender', 'zabeg22', 'zabeg23')
    list_editable = ( 'runner_age', 'runner_category', 'runner_gender', 'zabeg22', 'zabeg23')
    list_display = ('username', 'runner_team', 'runner_age', 'runner_category', 'runner_gender', 'zabeg22', 'zabeg23')
    # 'пробег_за_день','дистанция_за_день', 'время_пробега', 'средний_темп',)
    # list_display = ('user', 'runner_age', 'runner_category', 'runner_gender', 'is_admin', 'пробег_за_день', )
    list_display_links = ('username', 'runner_team')

    list_filter = ('runner_category', 'runner_team',)
    ordering = ('username', )

    list_per_page = 100
    list_max_show_all = 100


    def get_urls(self):
        urls = super().get_urls()
        urls.insert(-1, path('csv-upload/', self.upload_csv))
        return urls

    def upload_csv(self, request):
        if request.method == 'POST':
            form = UserImportForm(request.POST, request.FILES)
            if form.is_valid():
                # сохраняем загруженный файл и делаем запись в базу
                form_object = form.save()
                # обработка csv файла
                with form_object.csv_file.open('r') as csv_file:
                    rows = csv.reader(csv_file, delimiter=';')
                    # if next(rows)[:3] != ['team', 'runner', 'category']:
                    #     print(next(rows))
                    # #     # обновляем страницу пользователя
                    # #     # с информацией о какой-то ошибке
                    #     messages.warning(request, 'Неверные заголовки у файла')
                    #     return HttpResponseRedirect(request.path_info)
                    lst = []
                    for row in rows:
                        # # добавляем данные в базу
                        # User.objects.update_or_create(username=row[2])
                        # Teams.objects.update_or_create(team=row[0])
                        # team = Teams.objects.get(team=row[0])
                        # team.keywordclass_set.create(
                        #     kwteam=team,
                        #     kwteam_id=row[1],
                        #     keyword=row[2].lower()
                        # )

                        #
                        userid = User.objects.get(username=row[2])
                        # teamlist = Teams.objects.all()
                        # teamst = Teams.objects.filter(team__in=teamlist)
                        # if Teams.objects.get(team=row[0]):
                        #     team = Teams.objects.get(team=row[0])
                        #     team.runner_set.create(
                        #         runner_team=team,
                        #         runner_team_id=row[1],
                        #         runner_category=row[3],
                        #         runner_gender=row[4],
                        #         runner_age=row[5],
                        #         user_id=userid.id
                        #
                        #     )
                        # else:
                        #     team = Teams.objects.create(team=row[0])
                        #     team.runner_set.get_or_create(
                        #         runner_team=team,
                        #         runner_team_id=row[1],
                        #         runner_category=row[3],
                        #         runner_gender=row[4],
                        #         runner_age=row[5],
                        #         user_id=userid.id)
                        # # print(userid)
                        ## шаг 2 - запись по пробегам
                        usernumber = row[2]
                        listwithoutuser = row.copy()

                        del listwithoutuser[0:6]

                        ### print(listwithoutuser)
                        #
                        #

                        lst = [listwithoutuser[i:i + 4] for i in range(0, 120, 4)]
                        # lst.insert(0, usernumber)
                        # print(lst)
                        # userinbase= Runner.objects.get(user__username=row[0])
                        userid = User.objects.get(username=row[2])

                        for x in lst:

                            runner = RunnerDay.objects.get_or_create(
                                runner_id=userid.id-1,
                                day_select=x[0],
                                day_distance=x[1],
                                day_time=x[2],
                                day_average_temp=x[3]
                            )

                            # print(usernumber, x[0])

                        #
                        #
                        # # ## шаг 3 запись в статистику
                        # stats=Statistic.objects.create(
                        #     runner_id=userid.id-1,
                        #     team_id=row[1],
                        #     total_distance=0.0,
                        #     total_time="00:00:00",
                        #     total_average_temp="00:00:00" )
                        # #                        runner_category=row[2],
                        # #                        runner_team=team,
                        # #                        runner_gender=row[3],
                        # #                        runner_age=row[4])
                        #
                        #
                        #
                        # # Runner.objects.update_or_create(
                        # #     runner_team=row[0],
                        # #     user=row[1],
                        # #     runner_category=row[2],
                        #     runner_gender=row[3],
                        #     runner_age=row[4],
                        #
                        # )

                # конец обработки файлы
                # перенаправляем пользователя на главную страницу
                # с сообщением об успехе
                url = reverse('admin:index')
                messages.success(request, 'Файл успешно импортирован')
                return HttpResponseRedirect(url)
        form = UserImportForm()
        return render(request, 'admin/csv_import_page.html', {'form': form})


class RunnerDayAdmin(admin.ModelAdmin):
    search_fields = ('runner__user__username', 'day_select', 'day_distance', 'day_time', 'day_average_temp',
                     )
    list_editable = ('day_select', 'day_distance', 'day_time', 'day_average_temp',
                     )
    list_display = ('runner', 'day_select', 'day_distance', 'day_time', 'day_average_temp',
                    'get_photo_url', )
    list_display_links = ('runner',)

    list_filter = ('day_select',)
    ordering = ('day_select',)
    list_per_page = 100
    list_max_show_all = 100

    def get_photo_url(self, object):
        if object.photo:
            return mark_safe(f"<img src='{object.photo.url}' width=50>")

    get_photo_url.short_description = 'Миниатюра'

class StatisticAdmin(admin.ModelAdmin):
    search_fields = ('runner_stat', 'total_run', 'total_time', 'avg_temp',)

    list_display = ('runner_stat', 'total_run', 'total_time', 'avg_temp',)
    # list_display_links = ('user',)
    list_per_page = 100
    list_max_show_all = 100

    # ordering = ('общий_пробег', )
    #
    def total_run(self, username):
        from django.db.models import Sum
        total_distance = RunnerDay.objects.filter(runner__username=username).aggregate(Sum('day_distance'))
        # total_distance = Statistic.objects.filter(runner__u=username).aggregate(Sum('day_distance'))
        return total_distance['day_distance__sum']

    def total_time(self, username):
        from django.db.models import Sum
        total_time = RunnerDay.objects.filter(runner__username=username).aggregate(Sum('day_time'))
        return total_time['day_time__sum']

    def avg_temp(self, username):
        from django.db.models import Avg
        total_average_temp = RunnerDay.objects.filter(runner__username=username).aggregate(Avg('day_average_temp'))
        return total_average_temp['day_average_temp__avg']

    total_run.admin_order_field = 'total_distance'

    ordering = ('total_distance',)
    # всего_времени.admin_order_field = '-total_time'

admin.site.register(RunnerDay, RunnerDayAdmin)
admin.site.register(User, RunnerAdmin)
admin.site.register(Statistic, StatisticAdmin)
