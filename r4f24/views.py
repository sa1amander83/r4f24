import io
from django.forms import ModelForm
from django.shortcuts import redirect
from core.models import Teams
from profiles.models import RunnerDay, Statistic, UserImport
import pandas as pd
import csv
from django.http import HttpResponse


def export_runner_days(request):
    data = RunnerDay.objects.all().values('runner__username', 'day_select', 'day_distance', 'day_time',
                                          'day_average_temp', 'ball', 'number_of_run')

    df = pd.DataFrame(list(data))
    df.columns = ['Участник', 'День пробега', 'Дистанция за день', 'Время пробега', 'Средний темп', 'Баллы за пробежку',
                  'Номер пробежки']
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="runner_days.xlsx"'

    df.to_excel(response, index=False)

    return response


def export_statistic(request):
    data = Statistic.objects.all().values(
        'runner_stat__username', 'total_distance', 'total_time', 'total_average_temp', 'total_days', 'total_runs',
        'total_balls', 'is_qualificated'
    )
    df = pd.DataFrame(list(data))
    df.columns = ['Участник', 'Итоговый пробег', 'Общее время пробега', 'Средний темп', 'Дни пробега',
                  'Количество пробежек', 'Общая сумма баллов', 'Прошел квалификацию']
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="statistics.xlsx"'
    df.to_excel(response, index=False)
    return response


def import_teams(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('file')

        # Чтение данных из CSV файла
        decoded_file = csv_file.read().decode('utf-8',)
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)

        for row in reader:
            team_name = row.get('Team')
            keyword = row.get('Keyword')
            if team_name and keyword:
                Teams.objects.update_or_create(team=team_name, keyword=keyword)


        return redirect('index')




class UserImportForm(ModelForm):
    class Meta:
        model = UserImport
        fields = ('csv_file',)

