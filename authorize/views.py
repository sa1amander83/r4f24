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


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'register.html'
    success_url = reverse_lazy('authorize:login')

    def form_valid(self, form):
        runner_team = form.cleaned_data.get('runner_team__team')

        if runner_team:
            try:
                get_team = Teams.objects.get(team=runner_team)
                keyword_of_team = get_team.keyword

                # Validate user input
                if (form.cleaned_data['keyword'].lower() == keyword_of_team.lower() and
                        5 < int(form.cleaned_data['runner_age']) < 70 and
                        len(form.cleaned_data['username']) == 6 and
                        form.cleaned_data['username'][:3] == runner_team and
                        form.cleaned_data['username'].isnumeric()):

                    # Check if user already exists
                    if get_user_model().objects.filter(username=form.cleaned_data['username']).exists():
                        messages.error(self.request, 'Пользователь с таким именем уже существует.')
                        return self.form_invalid(form)  # Return to form with error

                    # Check if passwords match
                    password = form.cleaned_data.get('password')
                    password_confirm = form.cleaned_data.get(
                        'password_confirm')  # Assuming this field exists in your form

                    if password != password_confirm:
                        messages.error(self.request, 'Пароли не совпадают.')
                        return self.form_invalid(form)  # Return to form with error

                    # Save new user
                    user = form.save(commit=False)
                    user.runner_team_id = get_team.id
                    user.set_password(password)  # Ensure the password is hashed
                    user.save()
                    messages.success(self.request, 'Регистрация прошла успешно! Вы можете войти в систему.')
                    return redirect(self.success_url)

                else:
                    messages.error(self.request, 'Неверно указано кодовое слово или другие данные.')
                    return self.form_invalid(form)  # Return to form with error

            except Teams.DoesNotExist:
                messages.error(self.request, 'Неверная команда.')
                return self.form_invalid(form)  # Return to form with error

    def handle_invalid_registration(self, form):
        # Handle specific validation messages
        username = form.cleaned_data.get('username')
        runner_age = int(form.cleaned_data.get('runner_age', 0))

        if not username.isnumeric():
            messages.error(self.request, 'Имя пользователя должно состоять только из цифр')
        elif username[:3] != form.cleaned_data.get('runner_team__team'):
            messages.error(self.request, 'Номер участника не соответствует команде')
        elif runner_age < 5 or runner_age > 70:
            messages.error(self.request, 'Неверно указан возраст. Возраст должен быть от 5 до 70.')
        elif username and len(username) != 6:
            messages.error(self.request, 'Имя пользователя должно состоять из 6 цифр.')

        return redirect('authorize:register')

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return self.render_to_response({'form': form})
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
            team = request.POST.get("team")
            password = request.POST.get("password1")
            password2 = request.POST.get("password2")
            key = request.POST.get("keyword")

            getTeam = Teams.objects.get(team=username_form[:3])

            keywordOfTeam = getTeam.keyword.lower()

            try:
                username = get_user_model().objects.get(username=username_form)
            except ObjectDoesNotExist:
                messages.error(request,
                               'Участник с таким номером не найден')
                render(request, 'pass_reset.html', {'form': form})

            if key != keywordOfTeam.lower():
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
