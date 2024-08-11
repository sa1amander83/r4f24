import csv
from django.core.management.base import BaseCommand

from profiles.models import Statistic


class Command(BaseCommand):
    help = 'Export statistics to a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to output CSV file')

    def handle(self, *args, **options):
        csv_file = options['csv_file']

        # Получаем все записи из модели Statistic
        statistics = Statistic.objects.all()

        # Открываем CSV файл для записи
        with open(csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)

            # Записываем заголовки столбцов
            writer.writerow([
                'ID',
                'Участник',
                'Итоговый пробег',
                'Общее время пробега',
                'Средний темп за все время',
                'Дни пробега',
                'Количество пробежек',
                'Общая сумма баллов',
                'Прошел квалификацию'
            ])

            # Записываем данные
            for stat in statistics:
                writer.writerow([
                    stat.id,
                    stat.runner_stat.username,  # Предполагается, что у User есть поле username
                    stat.total_distance,
                    str(stat.total_time),
                    str(stat.total_average_temp),
                    stat.total_days,
                    stat.total_runs,
                    stat.total_balls,
                    stat.is_qualificated
                ])

        self.stdout.write(self.style.SUCCESS(f'Statistics exported successfully to {csv_file}'))