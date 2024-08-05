from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Avg, Count
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_POST
from django.views.generic import ListView, CreateView

from core.models import Group, User, Teams, GroupsResult, ComandsResult
from profiles.models import Statistic
from profiles.tasks import calc_start, calc_comands
from profiles.utils import DataMixin
from r4f24.forms import FamilyForm, AddFamilyForm


# просмотр группы участников


class MyGroup(ListView, DataMixin):
    model = Group
    template_name = 'mygroup.html'
    context_object_name = 'data'

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        group_users = {}
        group_stat = {}
        try:
            obj = get_user_model().objects.get(username=self.kwargs['username'])
            if 'mygroup' in self.request.path_info:
                group = obj.runner_group
                users = get_user_model().objects.filter(runner_group=group)
                group_stat = get_user_model().objects.filter(runner_group=obj.runner_group, not_running=False)
                flag = True

            else:
                group = obj.runner_team
                users = get_user_model().objects.filter(runner_team=group)
                group_stat = get_user_model().objects.filter(runner_team=obj.runner_team, not_running=False)
                flag = False

            if group:
                # получаем всех пользователей с этой группой или командой
                group_users[group] = []

                user_stats = Statistic.objects.filter(runner_stat__in=users)
                group_data = {}
                total_results = user_stats.aggregate(
                    total_balls=Sum('total_balls'),
                    total_distance=Sum('total_distance'),
                    total_time=Sum('total_time'),
                    total_average_temp=Avg('total_average_temp'),
                    total_days=Sum('total_days'),
                    total_runs=Sum('total_runs')
                )

                group_data[group] = {
                    'users': users,
                    'total_results': total_results,
                    'user_stats': user_stats
                }

                # Pass the data to the template

                context = {
                    'flag': flag,
                    'group_data': group_data
                }

                for user in group_stat:
                    try:
                        stats_obj = Statistic.objects.get(runner_stat_id=user.id)

                        group_users[group].append({
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
                    except:
                        continue

                context['qs'] = group_users
            else:
                context['message'] = 'Вы не состоите в группе'



        except:
            context['qs'] = None

        return context


# добавляем группу участнику если он в ней состоит

# def addRunnerToGroup(request, username, group):
#     if request.method == 'POST':
#         group_id = request.POST.get('group').id
#         group = get_object_or_404(User, id=request.user.id).runner_group
#
#         if group:
#             messages.warning(request, f'Вы уже входите  в эту группу: {group}.')
#         else:
#             group.runner_group = group_id
#             messages.success(request, f'Вы создали и добавились в группу{group.group_title}.')
#         return redirect('group_view', group_id=group.id)
#     else:
#         form = AddFamilyForm()
#         grp = group
#
#     groups = Group.objects.all()
#
#
#     return render(request, 'add_runner_to_group.html',
#                   {'groups': groups, 'group': grp, 'username': username, 'form': form})


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


class SuccessView(View):
    def get(self, request):
        return render(request, 'mygroup.html')


# @login_required
# def add_user_to_group(request, username, group_id):
#     group = Group.objects.get(id=group_id)
#     user = request.user
#     user.runner_group = group
#     user.save()
#     calc_comands.delay(username)
#     return redirect('groups:mygroup', username=username)


class GroupsListView(ListView):
    model = Group

    template_name = 'add_family.html'
    context_object_name = 'group'
    form = AddFamilyForm

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AddFamilyForm()
        return context

    def post(self, request, *args, **kwargs):
        form = AddFamilyForm(request.POST)
        print(form.cleaned_data)
        group = form.cleaned_data['group_title']
        print(group)

    def get_queryset(self):
        return Group.objects.all()


#
# class AddFamily(CreateView, LoginRequiredMixin):
#     model = Group
#     template_name = 'addfamily.html'
#     form_class = AddFamilyForm
#     success_url = reverse_lazy('profile:profile')
#
#     def get_context_data(self, *args, object_list=None, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#         return context
#
#
# def add_group(request, username):
#     families = Group.objects.all()
#
#     if request.method == 'POST' and Group.objects.filter(runner__runner_status=1):
#         form = FamilyForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('profile:family_list', request.user)
#
#     else:
#         form = FamilyForm()
#     return render(request, 'add_family.html', {'form': form, 'families': families})


# просмотр состава выбранной группы

def view_group(request, group):
    rankings = []
    group_data = {}
    if 'groups' in request.path_info:
        # groups = Group.objects.filter(group_title=group)
        group_id = Group.objects.get(id=group)
        group = group_id.group_title
        users = get_user_model().objects.filter(runner_group=group_id)
        group_count = GroupsResult.objects.all().count()
        # all_groups = Group.objects.all()
        grp_stats = GroupsResult.objects.all().order_by('-group_total_balls', 'group_total_distance').values_list(
            'group__group_title', 'group_total_balls')
        group_titles = list(grp_stats.values_list('group__group_title', flat=True))

        # If you want to see the total balls alongside the titles, you can keep it as is
        # or create a list of tuples as follows:
        group_stats_list = list(group_titles)

        flag = True


    else:
        group_id = Teams.objects.get(team=group)
        users = get_user_model().objects.filter(runner_team=group_id)
        group_count = ComandsResult.objects.all().count()
        flag = False
        comand_results = ComandsResult.objects.all().order_by('-comand_total_balls',
                                                              'comand_total_distance').values_list('comand__team',
                                                                                                   'comand_total_balls')
        group_titles = list(comand_results.values_list('comand__team', flat=True))
        group_stats_list = list(group_titles)

    # Calculate total results for groups
    user_stats = Statistic.objects.filter(runner_stat__in=users)

    total_results = user_stats.aggregate(
        total_balls=Sum('total_balls'),
        total_distance=Sum('total_distance'),
        total_time=Sum('total_time'),
        total_average_temp=Avg('total_average_temp'),
        total_days=Sum('total_days'),
        total_runs=Sum('total_runs'),
        tot_users=Count('runner_stat__username')

    )

    group_data[group] = {
        'users': users,
        'total_results': total_results,
        'user_stats': user_stats,

    }

    # Calculate total results for teams

    # Sort rankings based on total runs (or any other metric)
    rankings.sort(key=lambda x: x[1] if x[1] else 0, reverse=True)
    new_rank = rankings.sort(key=lambda x: x[0])

    # Create a ranking dictionary
    # ranking_data = {name: stats for name, stats in rankings}
    ranking_data = group_stats_list.index(group) + 1
    context = {
        'group_data': group_data, 'flag': flag, 'group_count': group_count, 'rank': ranking_data
    }
    return render(request, 'singlegroup.html', context)


@login_required
def group_list_and_create_view(request, username):
    can_create = False
    if request.method == 'POST':
        form = FamilyForm(request.POST)
        if form.is_valid():

            user = request.user
            if user.runner_group is not None:
                messages.success(request, f'Вы уже состоите в группе{user.runner_group}')
                return redirect('groups:mygroup', username)
            try:
                group = Group.objects.get(group_title=form.cleaned_data['group_title'])
                group = Group.objects.get(id=group.id)

                user.runner_group = group
                user.save()

            except:
                form.save()
                group = Group.objects.get(group_title=form.cleaned_data['group_title'])
                group = Group.objects.get(id=group.id)
                user = request.user
                user.runner_group = group
                user.save()

            calc_start.delay(user.id, user.username)

            messages.success(request, 'Group created successfully!')
            return redirect('groups:mygroup', username)
    else:
        user = get_user_model().objects.get(username=username)
        if user.can_create_group:
            can_create = True
        form = AddFamilyForm()
    groups = Group.objects.all()
    return render(request, 'group_list_and_create.html', {'groups': groups, 'form': form, 'can_create': can_create})


@login_required
@require_POST
def add_user_to_group(request):
    import json
    data = json.loads(request.body)
    group_id = data.get('group_id')
    group = get_object_or_404(Group, id=group_id)
    user = request.user
    user.runner_group = group
    user.save()
    calc_start.delay(user.id, user.username)
    redirect_url = reverse('groups:mygroup', kwargs={'username': user.username})
    return JsonResponse(
        data={'status': 'success', 'message': 'You have been added to the group', 'redirect_url': redirect_url})
