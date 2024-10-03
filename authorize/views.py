from django.contrib import messages
from django.contrib.auth import login, get_user_model, logout
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.contrib.sessions.backends.base import CreateError
from django.core.exceptions import ObjectDoesNotExist

from django.shortcuts import redirect, render

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import CreateView

from core.models import Teams
from r4f24.forms import RegisterUserForm, LoginUserForm, ResetForm

from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model

class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'register.html'
    success_url = reverse_lazy('authorize:login')


    def form_valid(self, form, **kwargs):
        runner_team = form.cleaned_data.get('runner_team__team')

        username = form.cleaned_data.get('username')
        if get_user_model().objects.filter(username=username).exists():
            messages.error(self.request, 'Пользователь с таким номером уже зарегистрирован.')
            return self.form_invalid(form)
        if runner_team:
            try:
                get_team = Teams.objects.get(team=runner_team)
                keyword_of_team = get_team.keyword

                # Get the username from cleaned data
                username = form.cleaned_data['username']


                # Proceed with other validations and registration
                if (form.cleaned_data['keyword'].lower() == keyword_of_team.lower() and
                        5 < int(form.cleaned_data['runner_age']) < 70 and
                        username[:3] == runner_team and
                        username.isnumeric()):

                    user = form.save(commit=False)
                    user.runner_team_id = get_team.id
                    user.save()
                    messages.success(self.request, 'Регистрация прошла успешно! Вы можете войти в систему.')
                    return redirect('authorize:login')

                # Additional validation checks...
                elif not username.isnumeric():
                    messages.error(self.request, 'Имя пользователя должно состоять только из цифр')
                elif username[:3] != runner_team:
                    messages.error(self.request, 'Номер участника не соответствует команде')
                elif form.cleaned_data.get('keyword').lower() != keyword_of_team.lower():
                    messages.error(self.request, 'Неверно указано кодовое слово.')
                elif not (5 < int(form.cleaned_data['runner_age']) < 70):
                    messages.error(self.request, 'Неверно указан возраст. Возраст должен быть от 5 до 70.')
                else:
                    messages.error(self.request, 'Неверно указано имя пользователя.')

            except Teams.DoesNotExist:
                messages.error(self.request, 'Неверная команда.')

        return redirect('authorize:register')  # Redirect if any validation fails

    #
    # def form_invalid(self, form):
    #     print(form.cleaned_data)
    #
    #
    #     username = form.cleaned_data.get('username')
    #
    #     if username:
    #         if get_user_model().objects.filter(username=username).exists():
    #             messages.error(self.request, 'Пользователь с таким именем уже существует.')
    #     else:
    #         messages.error(self.request, 'Имя пользователя не указано.')
    #
    #     return self.render_to_response(self.get_context_data(form=form))
class LoginUser(LoginView):
    authentication_form = LoginUserForm
    template_name = 'login.html'

    def get_success_url(self):
        return reverse_lazy("profile:profile", kwargs={'username': self.request.user})

    class Meta:
        model = get_user_model()
        fields = ['username', 'password']


def logout_user(request):
    logout(request)
    return redirect('authorize:login')


def show_reset(request):
    form = ResetForm()
    if request.method == "POST":
        try:
            username_form = request.POST.get("username")
            password = request.POST.get("password1")
            password2 = request.POST.get("password2")
            key = request.POST.get("keyword")

            getTeam = Teams.objects.get(team=username_form[:3])

            keywordOfTeam = getTeam.keyword

            try:
                username = get_user_model().objects.get(username=username_form)
            except ObjectDoesNotExist:
                messages.error(request,
                               'Участник с таким номером не найден')
                render(request, 'pass_reset.html', {'form': form})

            if key != keywordOfTeam:
                messages.error(request,
                               'Неверно указано кодовое слово')
                render(request, 'pass_reset.html', {'form': form})

            if password != password2:
                messages.error(request,
                               'Введенные пароли не совпадают')
                render(request, 'pass_reset.html', {'form': form})

            if key.lower() == keywordOfTeam and get_user_model().objects.get(
                    username=username_form) and password == password2:
                user = get_user_model().objects.get(username=username_form)
                try:
                    username = get_user_model().objects.get(username=username_form)
                except ObjectDoesNotExist:
                    messages.error(request,
                                   'Участник с таким номером не найден')
                    render(request, 'pass_reset.html', {'form': form})

                user.set_password(password)
                user.save()
                return redirect('authorize:login')
        except CreateError:
            pass

    return render(request, 'pass_reset.html', {'form': form})


def show_reset_success(request):
    return render(request, 'pass_updated.html')


def page_not_found_view(request, exception=None):
    return render(request, '404.html', status=404)
