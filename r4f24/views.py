
import csv
from urllib import response
from django.forms import ModelForm
from django.http import HttpResponse
from django.shortcuts import redirect, render

from core.models import Teams
from profiles.models import RunnerDay, Statistic, UserImport

class UserImportForm(ModelForm):
    class Meta:
        model = UserImport
        fields = ('csv_file',)

def exportcsv_runnerdays(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'

    writer = csv.writer(response, delimiter=";")
    writer.writerow(['uchastnik', 'ball','day', 'distance', 'time', 'average','num_of_run'])

    users = RunnerDay.objects.all().values_list('runner__username', 'vall','day_select', 'day_distance', 'day_time',
                                                'day_average_temp','number_of_run')
    try:
        for user in users:
            writer.writerow(user)
    except:
        pass

    return redirect('index')

def exportcsv_statistica(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'

    writer = csv.writer(response, delimiter=";")
    writer.writerow(['uchastnik', 'total_balls','total_distance', 'total_time', 'total_average','total_runs'])

    users = Statistic.objects.all().values_list('runner_stat__username','total_balls',  'total_distance', 'total_time',
                                                'total_average_temp','total_runs')
    
    for user in users:
        writer.writerow(user)
    
    return redirect('index')

def import_teams(request):
    if request.method == 'POST':
        form = UserImportForm(request.POST, request.FILES)
        if form.is_valid():
            # сохраняем загруженный файл и делаем запись в базу
            form_object = form.save()
            # обработка csv файла
            with form_object.csv_file.open('r') as csv_file:
                rows = csv.reader(csv_file, delimiter=';')
                for row in rows:
                    # # добавляем данные в базу
                    # User.objects.update_or_create(username=row[2])
                    Teams.objects.update_or_create(team=row[0])
                    # team = Teams.objects.get(team=row[0])
                    # team.keywordclass_set.create(
                    #     kwteam=team,
                    #     kwteam_id=row[1],
                    #     keyword=row[2].lower()

        return render(request, 'profile:profile')