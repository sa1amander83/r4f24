from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView

from core.models import Teams, KeyWordClass, CustomUser
from r4f24.forms import RegisterUserForm, LoginUserForm


def index(request):
    return render(request, 'base.html')


