import csv
from django.utils.encoding import force_str, smart_str

from profiles.models import RunnerDay


def export_to_csv(model_class, filename):
    # Получаем все записи модели
    records = model_class.objects.all()

    # Создаем список столбцов
    field_names = [field.name for field in model_class._meta.get_fields()]

    # Открываем файл для записи
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(field_names)  # Записываем заголовок столбцов

        # Перебираем каждую запись и записываем ее в CSV файл
        for record in records:
            row = []
            for field_name in field_names:
                value = getattr(record, field_name)
                if hasattr(value, '__iter__'):
                    value = list(value)
                else:
                    value = force_str(value)
                row.append(value)
            writer.writerow(row)

export_to_csv(RunnerDay, 'runner_days.csv')