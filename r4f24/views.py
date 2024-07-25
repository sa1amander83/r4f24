
import csv
import logging
import os
from pyexpat.errors import messages
from urllib import response
from django.forms import ModelForm
from django.http import HttpResponse
from django.shortcuts import redirect, render

from core.models import Teams
from profiles.models import RunnerDay, Statistic, UserImport
from r4f24.settings import BASE_DIR

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

        return redirect('index')
    

def uploadcsv(request):
    if request.method == 'GET':
            form = UserImportForm()
            return render(request, 'upload.html', {'form':form})

        # If not GET method then proceed
    try:
        form = UserImportForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'File is not CSV type')
                return redirect('import_teams')
            # If file is too large
            if csv_file.multiple_chunks():
                messages.error(request, 'Uploaded file is too big (%.2f MB)' %(csv_file.size(1000*1000),))
                return redirect('import_teams')

            # save and upload file 
            form.save()

            # get the path of the file saved in the server
            file_path = os.path.join(BASE_DIR, form.csv_file.url)

            # a function to read the file contents and save the product details
            save_new_product_from_csv(file_path)
            # do try catch if necessary
                
    except Exception as e:
        logging.getLogger('error_logger').error('Unable to upload file. ' + repr(e))
        messages.error(request, 'Unable to upload file. ' + repr(e))
    return redirect('import_teams')

def save_new_product_from_csv(file_path):
    # do try catch accordingly
    # open csv file, read lines
    with open(file_path, 'r') as fp:
        products = csv.reader(fp, delimiter=',')
        row = 0
        for product in products:
            if row==0:
                headers = product
                row = row + 1
            else:
                # create a dictionary of product details
                new_product_details = {}
                for i in range(len(headers)):
                    new_product_details[headers[i]] = product[i]

                # for the foreign key field you should get the object first and reassign the value to the key
                new_product_details['product'] = Teams.objects.get() # get the record according to value which is stored in db and csv file

                # create an instance of product model
                new_product = Teams()
                new_product.__dict__.update(new_product_details)
                new_product.save()
                row = row + 1
        fp.close()