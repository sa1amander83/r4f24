from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from django.forms import ModelForm, Form
from django.utils import timezone

from core.models import User, Group
from profiles.models import UserImport, RunnerDay, Photo
from multiupload.fields import MultiFileField, MultiMediaField, MultiImageField


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(
        attrs={'placeholder': "Введите номер",
               'class': 'w-full rounded-md border-gray-300 pl-10 text-sm focus:border-blue-500 focus:ring-blue-500',
               'id': 'username'}))
    # email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-input'}))
    runner_team__team = forms.CharField(label='Команда',
                                        widget=forms.TextInput(attrs={'placeholder': "Ваша команда",
                                                                      'class': 'w-full rounded-md border-gray-300 pl-10 text-sm focus:border-blue-500 focus:ring-blue-500',
                                                                      'id': 'team', 'readonly': 'true'}))
    keyword = forms.CharField(label='Кодовое слово',
                              widget=forms.TextInput(attrs={'placeholder': "Введите кодовое слово",
                                                            'class': 'w-full rounded-md border-gray-300 pl-10 text-sm focus:border-blue-500 focus:ring-blue-500'}))
    runner_age = forms.CharField(label='Возраст',
                                 widget=forms.TextInput(attrs={'placeholder': "Укажите свой возраст от 5 до 70",
                                                               'class': 'w-full rounded-md border-gray-300 pl-10 text-sm focus:border-blue-500 focus:ring-blue-500',
                                                               'type': 'number', 'id': 'runner_age'}))
    # runner_status = forms.BooleanField(widget=forms.RadioSelect(choices=(('Участник','Член семьи участника'),), attrs={'class': 'form-control form-control-user', 'id': 'status'}))
    password1 = forms.CharField(label='Пароль',
                                widget=forms.PasswordInput(attrs={'placeholder': "Введите пароль",
                                                                  'class': 'w-full rounded-md border-gray-300 pl-10 text-sm focus:border-blue-500 focus:ring-blue-500'}))
    password2 = forms.CharField(label='Повтор пароля',
                                widget=forms.PasswordInput(attrs={'placeholder': "Введите пароль еще раз",
                                                                  'class': 'w-full rounded-md border-gray-300 pl-10 text-sm focus:border-blue-500 focus:ring-blue-500'}))

    class Meta:
        model = User

        widgets = {

            'runner_gender': forms.Select(attrs={
                'class': 'w-full rounded-md border-gray-300 py-2 pl-10 text-sm focus:border-blue-500 focus:ring-blue-500'}),
            'runner_category': forms.Select(attrs={
                'class': 'w-full rounded-md border-gray-300 py-2 pl-10 text-sm focus:border-blue-500 focus:ring-blue-500'}),
            'zabeg22': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-blue-100 border-blue-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-blue-800 focus:ring-2  dark:border-blue-600'}),
            'zabeg23': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-blue-100 border-blue-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-blue-800 focus:ring-2  dark:border-blue-600'})
        }
        fields = (
            'username', 'runner_team__team', 'keyword', 'runner_age', 'runner_gender',
            'runner_category',
            'password1', 'password2', 'zabeg22', 'zabeg23')


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'placeholder': "Ведите имя",
                                                                            'class': 'w-full rounded-md border-gray-300 pl-10 text-sm focus:border-sky-500 focus:ring-sky-500'}))
    password = forms.CharField(label='Пароль',
                               widget=forms.PasswordInput(attrs={'placeholder': "Введите свой пароль",
                                                                 'class': 'w-full rounded-md border-gray-300 pl-10 text-sm focus:border-sky-500 focus:ring-sky-500'}))

    class Meta:
        model = get_user_model()
        fields = ['username', 'password']


class UserImportForm(ModelForm):
    class Meta:
        model = UserImport
        fields = ('csv_file',)


# class MyAverage(forms.TimeInput):
#     input_type = 'time'
#     format = '%M:%S'
#     TIME_INPUT_FORMAT = ['%M:%S']


# class MyTotalTimeInput(forms.TimeInput):
#     input_type = 'time'
#     format = '%H:%M:%S'


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


from datetime import date


class RunnerDayForm(ModelForm):
    class Meta:
        # day_time = forms.TimeField(help_text='00:00:00')
        # day_average_temp = forms.TimeField(help_text="00:00:00")
        model = RunnerDay

        # current_date = date.today()
        # date16 = datetime.date(2023, 7, 10)
        # date17 = datetime.date(2023, 9, 17)
        # photo = MultipleFileField(widget=MultipleFileInput(attrs={'class': 'form-control form-control-user'}))
        # photo = forms.FileField(widget=forms.ClearableFileInput(attrs={'allow_multiple_selected': True}))
        # if date
        # photo = MultipleFileField(label='Выберите файлы', required=False)

        widgets = {

            'day_select': forms.Select(attrs={
                'class': 'w-full rounded-md border-gray-300 py-2 pl-10 text-sm focus:border-blue-500 focus:ring-blue-500',
                'type': 'date', 'id': 'day_id'}),
            # 'number_of_run': forms.Select(attrs={'label':'False','class': 'form-control form-control-user', 'id': 'number_of_run_id'}),
            'day_distance': forms.NumberInput(
                attrs={
                    'class': 'w-full rounded-md border-gray-300 pl-10 text-sm focus:border-blue-500 focus:ring-blue-500',
                    'id': 'day_distance', 'placeholder': 'например 12,1'}),
            'day_time': forms.TextInput(
                attrs={'placeholder': "ЧЧ:ММ:СС",
                       'class': 'w-full rounded-md border-gray-300 pl-10 text-sm focus:border-blue-500 focus:ring-blue-500',
                       'id': 'day_time', 'step': '1'}),
            'day_average_temp': forms.TextInput(
                attrs={'placeholder': "ЧЧ:ММ:СС",
                       'class': 'w-full rounded-md border-gray-300 pl-10 text-sm focus:border-blue-500 focus:ring-blue-500',
                       'step': '1',

                       'id': 'temp'}),
            'ball': forms.NumberInput(
                attrs={
                    'class': 'w-full rounded-md border-gray-300 pl-10 text-sm focus:border-blue-500 focus:ring-blue-500',
                    'readonly': 'True', 'id': 'ball', 'placeholder': '00'}),

            'run_url': forms.URLInput(attrs={
                'class': 'w-full rounded-md border-gray-300 pl-10 text-sm focus:border-blue-500 focus:ring-blue-500',
                'id': 'run_url', 'placeholder': 'например https://www.runkeeper.com/app'}),

        }
        fields = ['day_select', 'day_distance', 'day_time', 'day_average_temp', 'ball', 'run_url']

    photo = MultiFileField(min_num=1, max_num=6, max_file_size=32048 * 32048 * 5)

    # def save(self, commit=True):
    #     instance = super(RunnerDayForm, self).save(commit)
    #     for each in self.cleaned_data['files']:
    #         Photo.objects.create(file=each, message=instance)
    #
    #     return instance


class AddFamilyForm(ModelForm):
    class Meta:
        model = Group
        group_title = forms.CharField(label='Название группы',
                                      widget=forms.TextInput(attrs={'placeholder': "Введите название",
                                                                    'class': 'w-full rounded-md border-gray-300 pl-10 text-sm focus:border-blue-500 focus:ring-blue-500',
                                                                    'autofocus': 'on', 'id': 'confirm-join-group'}))
        fields = ['group_title']


class FamilyForm(forms.ModelForm):
    class Meta:
        model = Group
        group_title = forms.CharField(label='Название группы', widget=forms.TextInput(
            attrs={'placeholder': "Введите название",
                   'class': 'w-full rounded-md border-gray-300 pl-10 text-sm focus:border-blue-500 focus:ring-blue-500',
                   'autofocus': 'on'}))
        fields = ('group_title',)


# class JoinGroupForm(forms.Form):
#     join_group = forms.BooleanField(
#         required=True,
#         widget=forms.widgets.B(
#             choices=[(True, "Yes"), (False, "No")]
#         )
#     )
# class GroupChoiceForm(forms.ModelForm):
#     class Meta:
#         model = Group
#         fields = ['choice']
#         labels = {'choice': ''}
#         widgets = {'choice': forms.CheckboxInput()}
class ResetForm(Form):
    username = forms.CharField(label='Логин', widget=forms.TextInput(
        attrs={'placeholder': "Введите имя",
               'class': 'w-full rounded-md border-gray-300 pl-10 text-sm focus:border-blue-500 focus:ring-blue-500',
               'autofocus': 'on'}))
    # email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-input'}))

    keyword = forms.CharField(label='Кодовое слово',
                              widget=forms.PasswordInput(attrs={'placeholder': "Ведите кодовое слово",
                                                                'class': 'w-full rounded-md border-gray-300 pl-10 text-sm focus:border-blue-500 focus:ring-blue-500',
                                                                'autocomplete': 'current-password'}))

    password1 = forms.CharField(label='Пароль',
                                widget=forms.PasswordInput(attrs={'placeholder': "Minimum 8 characters",
                                                                  'class': 'w-full rounded-md border-gray-300 pl-10 text-sm focus:border-blue-500 focus:ring-blue-500',
                                                                  'autocomplete': 'current-password'}))
    password2 = forms.CharField(label='Повтор пароля',
                                widget=forms.PasswordInput(attrs={'placeholder': "Minimum 8 characters",
                                                                  'class': 'w-full rounded-md border-gray-300 pl-10 text-sm focus:border-blue-500 focus:ring-blue-500',
                                                                  'autocomplete': 'current-password'}))

    class Meta:
        model = User
        fields = ('username', 'keyword', 'password1', 'password2')