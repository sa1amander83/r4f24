import csv
from django.core.management.base import BaseCommand

from profiles.models import RunnerDay


#python manage.py export_rundays rundays.csv
class Command(BaseCommand):
    help = 'Export runner days to a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to output CSV file')

    def handle(self, *args, **options):
        csv_file = options['csv_file']

        # Получаем все записи из модели RunnerDay
        runner_days = RunnerDay.objects.all()

        # Открываем CSV файл для записи
        with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # Записываем заголовки столбцов
            writer.writerow([
                'ID',
                'Участник',
                'День пробега',
                'Дистанция за день',
                'Время пробега',
                'Средний темп',
                'Баллы за пробежку',
                'Номер пробежки'
            ])

            # Записываем данные
            for runner_day in runner_days:
                writer.writerow([
                    runner_day.id,
                    runner_day.runner.username,  # Предполагается, что у User есть поле username
                    runner_day.day_select,
                    runner_day.day_distance,
                    str(runner_day.day_time),
                    str(runner_day.day_average_temp),
                    runner_day.ball,
                    runner_day.number_of_run
                ])

        self.stdout.write(self.style.SUCCESS(f'Runner days exported successfully to {csv_file}'))
