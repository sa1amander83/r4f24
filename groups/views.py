from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect


# Create your views here.
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView

from core.models import Group, User
from profiles.models import Statistic
from profiles.utils import DataMixin
from r4f24.forms import FamilyForm, AddFamilyForm, GroupChoiceForm


class MyGroup(ListView, DataMixin):
    model = Group
    template_name = 'mygroup.html'
    context_object_name = 'data'

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        group_users = {}
        # поулчаем группу через юезра из кварг
        try:
            obj = User.objects.get(username=self.kwargs['username'])

            group = obj.runner_group
            if group is not None:
            # получаем всех пользователей с этой группой
                group_stat = User.objects.filter(runner_group=obj.runner_group)


                group_users[obj.runner_group] = []

                for user in group_stat:
                    stats_obj = Statistic.objects.get(runner_stat_id=obj.id)
                    group_users[obj.runner_group].append({
                        'group': str(group),
                        'user': user.username,
                        'total_distance': stats_obj.total_distance,
                        'total_time': stats_obj.total_time,
                        'total_average_temp': stats_obj.total_average_temp,
                        'total_days': stats_obj.total_days,
                        'total_runs': stats_obj.total_runs,
                        'total_balls': stats_obj.total_balls,
                        'is_qualificated': stats_obj.is_qualificated
                    })
                context['qs'] = group_users
            else:
                context['message']='Вы не состоите в группе'



        except:
            context['qs'] = None

        return context
#добавляем группу участнику если он в ней состоит

def addRunnerToGroup(request, username, group):
    if request.method == 'POST':
        group_id = request.POST.get('group').id
        group = get_object_or_404(User, id=request.user.id).runner_group

        if group:
            messages.warning(request, f'Вы уже входите  в эту группу: {group}.')
        else:
            group.runner_group=group_id
            messages.success(request, f'Вы создали и добавились в группу{group.group_title}.')
        return redirect('group_view', group_id=group.id)
    else:
        form=AddFamilyForm()
        grp=group

    groups = Group.objects.all()
    return render(request, 'add_runner_to_group.html', {'groups': groups, 'group':grp, 'usernmae':username, 'form':form})

# def join_group_view(request):
#     if request.method == 'POST':
#         form = JoinGroupForm(request.POST)
#         if form.is_valid():
#             join_group = form.cleaned_data['join_group']
#             if join_group:
#                 # Add the user to the group
#                 # ...
#                 return redirect('success_url')
#             else:
#                 # Do nothing
#                 return redirect('decline_url')
#     else:
#         form = JoinGroupForm()
#
#     return render(request, 'join_group.html', {'form': form})

def group_choice_view(request, group_name):
    if request.method == 'POST':
        form = GroupChoiceForm(request.POST)
        if form.is_valid():
            choice = form.cleaned_data['choice']
            if choice:
                # Добавление пользователя в группу
                user = request.user
                try:
                    existing_choice = Group.objects.get(user=user, group=group_name)
                except Group.DoesNotExist:
                    existing_choice = None
                if existing_choice and not existing_choice.choice:
                    existing_choice.choice = True
                    existing_choice.save()
                else:
                    Group.objects.create(user=user, group=group_name, choice=True)
            # else:
            #     # Удаление пользователя из группы
            #     Group.objects.filter(user=user, group=group_name).delete()
            return redirect('groups:mygroup')
    else:

        form = GroupChoiceForm()
    return render(request, 'add_runner_to_group.html', {'form': form})

class SuccessView(View):
    def get(self, request):
        return render(request, 'mygroup.html')

class GroupsListView(ListView):
    model = Group
    template_name = 'add_family.html'
    context_object_name = 'group'
    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    def get_queryset(self):
        return Group.objects.all()




class AddFamily(CreateView, LoginRequiredMixin):
    model = Group
    template_name = 'addfamily.html'
    form_class = AddFamilyForm
    success_url = reverse_lazy('profile:profile')

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        return context




def add_group(request, username):
    families = Group.objects.all()

    if request.method == 'POST' and Group.objects.filter(runner__runner_status=1):
        form = FamilyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('profile:family_list', request.user )





    else:
        form = FamilyForm()
    return render(request, '../groups/templates/add_family.html', {'form': form, 'families':families})

def family_list(request, username):
    families = Group.objects.all()

    return render(request, '../groups/templates/family_list.html', {'families': families, 'username':request.user.username})

