from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from django.forms import ModelForm

from core.models import User, Family
from profiles.models import UserImport, RunnerDay


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(
        attrs={'class': 'form-control form-control-user', 'id': 'username'}))
    # email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-input'}))
    runner_team = forms.CharField(label='Команда',
                                  widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'team'}))
    keyword = forms.CharField(label='Кодовое слово',
                              widget=forms.TextInput(attrs={'class': 'form-control form-control-user'}))

    password1 = forms.CharField(label='Пароль',
                                widget=forms.PasswordInput(attrs={'class': 'form-control form-control-user'}))
    password2 = forms.CharField(label='Повтор пароля',
                                widget=forms.PasswordInput(attrs={'class': 'form-control form-control-user'}))

    class Meta:
        model = User
        fields = ('username', 'runner_team', 'keyword', 'runner_age', 'runner_gender', 'runner_category', 'password1',
                  'password2', 'zabeg22', 'zabeg23')
        widgets = {

        }


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


class MyTotalTimeInput(forms.TimeInput):
    input_type = 'time'
    format = '%H:%M:%S'

class RunnerDayForm(ModelForm):
    class Meta:
        day_time = forms.TimeField(help_text='00:00:00')
        day_average_temp = forms.TimeField(help_text="00:00:00")
        model = RunnerDay

        # current_date = date.today()
        # date16 = datetime.date(2023, 7, 10)
        # date17 = datetime.date(2023, 9, 17)

        # if date

        fields = ['day_select', 'day_distance', 'day_time', 'day_average_temp', 'photo']

        widgets = {
            'day_select': forms.Select(attrs={'class': 'form-control form-control-user', 'id': 'day_id'}),
            'day_distance': forms.NumberInput(attrs={'class': 'form-control form-control-user', 'value': '10'}),
            # 'day_time': forms.TimeInput(attrs={'class': 'form-control form-control-user','value':'00:00:00'}),
            'day_time': MyTotalTimeInput(attrs={'class': 'form-control form-control-user', 'step': '1', 'value':'01:00:00'}),
            # 'day_average_temp': forms.TimeInput(attrs={'class': 'form-control form-control-user','value':'00:00:00','format':'%H:%i:%s'}),
            'day_average_temp': MyAverage(
                attrs={'class': 'form-control form-control-user', 'format': '%m:%s','value':'00:05:00', 'step': '1'}),
            # 'calory': forms.NumberInput(
            #     attrs={'class': 'form-control form-control-user', 'value': '00.000', 'id': 'calory_id'}),
            'photo': forms.FileInput(attrs={'class': 'form-control form-control-user'}),
        }

class AddFamilyForm(ModelForm):

    class Meta:
        model = Family
        fields=['runner_family']