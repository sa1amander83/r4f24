from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms

from core.models import CustomUser


class RegisterUserForm(UserCreationForm):

    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-control form-control-user', 'id':'username'}))
    # email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-input'}))
    team = forms.CharField(label='Команда',widget= forms.TextInput(attrs={'disabled':'disabled','id':'team'}))
    keyword = forms.CharField(label='Кодовое слово',
                              widget=forms.TextInput(attrs={'class': 'form-control form-control-user'}))

    password1 = forms.CharField(label='Пароль',
                                widget=forms.PasswordInput(attrs={'class': 'form-control form-control-user'}))
    password2 = forms.CharField(label='Повтор пароля',
                                widget=forms.PasswordInput(attrs={'class': 'form-control form-control-user'}))

    class Meta:
        model = CustomUser
        fields = ('username', 'team','keyword', 'runner_age', 'runner_gender','runner_category','password1', 'password2',  'zabeg22', 'zabeg23')


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-control form-control-user'}))
    password = forms.CharField(label='Пароль',
                               widget=forms.PasswordInput(attrs={'class': 'form-control form-control-user'}))
