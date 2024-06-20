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
        attrs={'class': 'form-control form-control-user', 'id': 'username'}))
    # email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-input'}))
    runner_team = forms.CharField(label='Команда',
                                  widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'team'}))
    keyword = forms.CharField(label='Кодовое слово',
                              widget=forms.TextInput(attrs={'class': 'form-control form-control-user'}))
    # runner_status = forms.ChoiceField(widget=forms.RadioSelect(attrs={'class': 'form-control form-control-user', 'id': 'status'}))
    password1 = forms.CharField(label='Пароль',
                                widget=forms.PasswordInput(attrs={'class': 'form-control form-control-user'}))
    password2 = forms.CharField(label='Повтор пароля',
                                widget=forms.PasswordInput(attrs={'class': 'form-control form-control-user'}))

    class Meta:
        model = User

        widgets = {
        'runner_status': forms.RadioSelect(attrs={'class': 'form-control form-control-user', 'id': 'status'})
        }
        fields = (
        'username', 'runner_status', 'runner_team', 'keyword', 'runner_age', 'runner_gender', 'runner_category',
        'password1','password2', 'zabeg22', 'zabeg23')

class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-control form-control-user'}))
    password = forms.CharField(label='Пароль',
                               widget=forms.PasswordInput(attrs={'class': 'form-control form-control-user'}))

    class Meta:
        model = get_user_model()
        fields = ['username', 'password']


class UserImportForm(ModelForm):
    class Meta:
        model = UserImport
        fields = ('csv_file',)


class MyAverage(forms.TimeInput):
    input_type = 'time'
    format = '%M:%S'
    TIME_INPUT_FORMAT=['%M:%S']


class MyTotalTimeInput(forms.TimeInput):
    input_type = 'time'
    format = '%H:%M:%S'


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


class RunnerDayForm(ModelForm):


    class Meta:
        day_time = forms.TimeField(help_text='00:00:00')
        day_average_temp = forms.TimeField(help_text="00:00:00")
        model = RunnerDay


        # current_date = date.today()
        # date16 = datetime.date(2023, 7, 10)
        # date17 = datetime.date(2023, 9, 17)
        # photo = MultipleFileField(widget=MultipleFileInput(attrs={'class': 'form-control form-control-user'}))
        # photo = forms.FileField(widget=forms.ClearableFileInput(attrs={'allow_multiple_selected': True}))
        # if date
        # photo = MultipleFileField(label='Выберите файлы', required=False)

        widgets = {

            'day_select': forms.Select(attrs={'class': 'form-control form-control-user', 'id': 'day_id'}),
            # 'number_of_run': forms.Select(attrs={'label':'False','class': 'form-control form-control-user', 'id': 'number_of_run_id'}),
            'day_distance': forms.NumberInput(
                attrs={'class': 'form-control form-control-user', 'value': '5', 'id': 'day_distance'}),
            'day_time': MyTotalTimeInput(
                attrs={'class': 'form-control form-control-user', 'step': '1', 'value': '00:15:00'}),
            'day_average_temp': MyAverage(
                attrs={'class': 'form-control form-control-user', 'type':'time', 'step': '1','value':'00:04:00',
                       'id': 'temp'}),
            'ball': forms.NumberInput(attrs={'class': 'form-control', 'readonly':'True','id':'ball', 'placeholder':'00'}),



        }
        fields = ['day_select',  'day_distance', 'day_time', 'day_average_temp', 'ball']

    photo = MultiFileField(min_num=1, max_num=6, max_file_size=2048 * 2048 * 5)

    # def save(self, commit=True):
    #     instance = super(RunnerDayForm, self).save(commit)
    #     for each in self.cleaned_data['files']:
    #         Photo.objects.create(file=each, message=instance)
    #
    #     return instance


class AddFamilyForm(ModelForm):
    class Meta:
        model = Group
        fields = ['group_title']


class FamilyForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('group_title',)
# class JoinGroupForm(forms.Form):
#     join_group = forms.BooleanField(
#         required=True,
#         widget=forms.widgets.B(
#             choices=[(True, "Yes"), (False, "No")]
#         )
#     )
class GroupChoiceForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['choice']
        labels = {'choice': ''}
        widgets = {'choice': forms.CheckboxInput()}
class ResetForm(Form):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-control form-control-user','id':'id_username', 'autocomplete':'username', 'autofocus':'on'}))
    # email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-input'}))

    keyword = forms.CharField(label='Кодовое слово',
                              widget=forms.PasswordInput(attrs={'class': 'form-control form-control-user', 'autocomplete':'current-password'}))

    password1 = forms.CharField(label='Пароль',
                                widget=forms.PasswordInput(attrs={'class': 'form-control form-control-user', 'autocomplete':'current-password'}))
    password2 = forms.CharField(label='Повтор пароля',
                                widget=forms.PasswordInput(attrs={'class': 'form-control form-control-user', 'autocomplete':'current-password'}))


    class Meta:
        model = User
        fields = ('username', 'keyword', 'password1', 'password2')