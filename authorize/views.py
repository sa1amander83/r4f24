from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import CreateView

from core.models import Teams, CustomUser, KeyWordClass
from r4f24.forms import RegisterUserForm, LoginUserForm


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'register.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        # c_def = self.get_user_context(title="Регистрация")
        # # context['msgerror']='неверно указано кодовое слово'
        return context

    def post(self, request, *args, **kwargs):
        request_keep = RegisterUserForm(request.POST)
        if request_keep.is_valid():
            request_keep.save(commit=False)
            request_keep.username = self.request.user
            # request_keep.post_time_create = "some value"
            # request_keep.post_time_update = "some value"
            request_keep.save()
            return redirect('login')
    # # return render(request, 'sitelogic/addpost.html', context={'form': request_keep})
    # def get_kw(self, form):
    #     # form= RegisterUserForm
    #     getTeam = Teams.objects.filter(team=form.cleaned_data['username'][:3])
    #     print(getTeam)
    #     keywordOfTeam = str(KeyWordClass.objects.get(kwteam_id__exact=getTeam[0]))
    #
    #     if form.cleaned_data['keyword'] == keywordOfTeam:
    #         self.form_valid(form)
    #     else:
    #         raise ValidationError('неверно введено кодовое слово')
    #     return redirect('register')
    #
    def form_invalid(self, form):
        getTeam = Teams.objects.filter(team=form.cleaned_data['username'][:3])
        print(getTeam)
        keywordOfTeam = KeyWordClass.objects.get(kwteam_id__exact=getTeam[0])
        print(form.cleaned_data['keyword'], keywordOfTeam )
        print(keywordOfTeam )
        print(str(form.cleaned_data['keyword']) == keywordOfTeam)
        if form.cleaned_data['keyword'] == keywordOfTeam:

            self.form_valid()
        else:
            raise ValidationError('неверно введено кодовое слово')
        return redirect('register')

    def form_valid(self, form, **kwargs):
        getTeam = Teams.objects.filter(team=form.cleaned_data['username'][:3])
        keywordOfTeam = str(KeyWordClass.objects.get(kwteam_id__exact=getTeam[0]))

        if form.cleaned_data['keyword'].lower() == keywordOfTeam:
            user = form.save()
            login(self.request, user)

            return redirect('login', user)
        else:
            messages.error(self.request, 'Неверно указано кодовое слово')
        return redirect('register')

    def get_user_context(self, title):
        pass


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'login.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

    def get_success_url(self):

        return reverse_lazy('profile', self.request.user)

    def form_valid(self, form):

        form_data = form.cleaned_data

        form_data['data'] = form.cleaned_data['username']

        getuser = CustomUser.objects.get(username=form.cleaned_data['username'])
        # print(getuser)
        # if getuser.pk == 1:
        #     login(self.request, getuser)

        obj = get_object_or_404(CustomUser, pk=getuser.pk )
        print(obj)
        if obj:
            login(self.request, getuser)
            return redirect('profile', getuser)

        else:
            return redirect('register', runner=form_data['username'])