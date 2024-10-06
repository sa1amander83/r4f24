import csv

from attr.filters import exclude
from django.contrib.auth import get_user_model
from django.db import models, IntegrityError
from django.db.models import Q, Sum, Count, ExpressionWrapper, TimeField, F, Avg, Window, Value, CharField

from django.db.models.functions import Cast, RowNumber
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.cache import cache_page

from django.views.generic import ListView
from core.models import User, Teams, Group, GroupsResult, ComandsResult
from profiles.models import Statistic, RunnerDay, Championat
from profiles.utils import DataMixin


class IndexView(DataMixin, ListView):
    model = Statistic
    template_name = 'index.html'
    context_object_name = 'stat'
    from django.db.models import Count, Case, When, IntegerField, Q
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        context['user_detail'] = get_user_model().objects.filter(id=self.request.user.id)
        context['cat_selected'] = 0
        context['age'] = 0
        context['fem'] = get_user_model().objects.filter(not_running=False, runner_gender='ж').count()
        context['men'] = get_user_model().objects.filter(not_running=False, runner_gender='м').count()
        context['new'] = get_user_model().objects.filter(not_running=False, runner_category=1).count()
        context['mid'] = get_user_model().objects.filter(not_running=False, runner_category=2).count()
        context['hi'] = get_user_model().objects.filter(not_running=False, runner_category=3).count()
        context['count_of_runners'] = get_user_model().objects.exclude(not_running=True).count()

        context['tot_dist'] = Statistic.objects.filter(runner_stat__not_running=False). \
            values('runner_stat__username', 'total_time', 'total_distance', 'runner_stat__runner_gender',
                   'runner_stat__runner_category', 'total_balls_for_champ',
                   'runner_stat__runner_group', 'total_runs', 'total_balls', 'total_average_temp').order_by(
            '-total_balls', '-total_distance')

        return context


class CatListView(DataMixin, ListView):
    model = User
    template_name = 'total.html'
    context_object_name = 'comand'

    def get_queryset(self):
        return Teams.objects.all()

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        category_selected = self.kwargs['cat']
        context['cat'] = category_selected

        if category_selected:
            all_teams = Teams.objects.all().values_list('team', flat=True)
            all_runners = get_user_model().objects.all()

            comand_list = dict()

            for v in all_teams:
                teamsss = RunnerDay.objects.filter(runner__runner_team__team=v).filter(
                    day_average_temp__lte="00:08:00"). \
                    values('runner__user__username', 'runner__runner_category', 'runner__runner_team'). \
                    annotate(  # отсеиваем средний темп меньше 7
                    total_dist=Sum('day_distance'), total_time=Sum('day_time'),
                    avg_time=Avg('day_average_temp')).aggregate(Sum('total_dist'), Sum('total_time'), Avg('avg_time'))
                comand_list[v] = teamsss
            # filter(runner__runner_category=category_selected).\
            context['comand_list'] = comand_list
            return context


        else:
            pass  # сумма по всем категориям


class RunnersCatView(DataMixin, ListView):
    model = RunnerDay
    template_name = 'category.html'
    context_object_name = 'stat'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        cat_selected = self.kwargs['cat']
        context['cat_selected'] = cat_selected

        context['tot_dist'] = Statistic.objects.filter(runner_stat__not_running=False,
                                                       runner_stat__runner_category=cat_selected).values(
            'runner_stat__username', 'runner_stat__runner_team__team', 'runner_stat__runner_group__group_title',
            'total_runs',
            'total_time',
            'total_balls', 'total_days', 'total_distance', 'total_average_temp').order_by('-total_balls')

        return context


def get_queryset(self):
    return RunnerDay.objects.all()


class RunnersCatAgeView(DataMixin, ListView):
    model = RunnerDay
    template_name = 'category.html'
    context_object_name = 'stat'

    def get_context_data(self, *, object_list=None, **kwargs):
        global start_age, last_age, get_age
        context = super().get_context_data(**kwargs)
        cat_selected = self.kwargs['cat']
        context['cat_selected'] = cat_selected

        get_age = self.kwargs['age']

        # Define age ranges based on 'get_age'
        if get_age == 0:
            start_age = 4
            last_age = 99
        elif get_age == 1:
            start_age = 4
            last_age = 17
        elif get_age == 2:
            start_age = 18
            last_age = 35
        elif get_age == 3:
            start_age = 36
            last_age = 49
        elif get_age == 4:
            start_age = 50
            last_age = 99

        # Filtering logic based on selected category
        if cat_selected in [1, 2]:  # Assuming these are categories for women
            context['tot_dist'] = Statistic.objects.filter(
                runner_stat__runner_category=cat_selected,
                runner_stat__runner_age__gte=start_age,
                runner_stat__runner_age__lte=last_age,
                runner_stat__not_running=False
            ).values(
                'runner_stat__username',
                'runner_stat__runner_team__team',
                'runner_stat__runner_gender',
                'runner_stat__runner_group__group_title',
                'total_runs',
                'total_time',
                'total_balls_for_champ',
                'total_balls',
                'total_days',
                'total_distance',
                'total_average_temp'
            ).order_by('-total_balls')  # Order by total_balls for categories 1 and 2

        elif cat_selected == 3:  # Assuming this is for male participants
            context['tot_dist'] = Statistic.objects.filter(
                runner_stat__runner_category=3,
                runner_stat__runner_age__gte=start_age,
                runner_stat__runner_age__lte=last_age,
                runner_stat__not_running=False
            ).values(
                'runner_stat__username',
                'runner_stat__runner_team__team',
                'runner_stat__runner_gender',
                'runner_stat__runner_group__group_title',
                'total_runs',
                'total_time',
                'total_balls_for_champ',
                'total_balls',
                'total_days',
                'total_distance',
                'total_average_temp'
            ).order_by('-total_balls_for_champ')  # Order by total_balls_for_champ for category 3

        else:  # For other categories or default case
            context['tot_dist'] = Statistic.objects.filter(
                runner_stat__runner_age__gte=start_age,
                runner_stat__runner_age__lte=last_age,
                runner_stat__not_running=False
            ).values(
                'runner_stat__username',
                'runner_stat__runner_team__team',
                'runner_stat__runner_gender',
                'runner_stat__runner_group__group_title',
                'total_runs',
                'total_time',
                'total_balls',
                'total_days',
                'total_distance',
                'total_balls_for_champ',
                'total_average_temp'
            ).order_by('-total_balls')  # Default ordering

        return context


class RunnersCatGenderView(DataMixin, ListView):
    model = RunnerDay
    template_name = 'category.html'
    context_object_name = 'stat'

    def get_context_data(self, *, object_list=None, **kwargs):
        global start_age, last_age, get_gender, get_age
        context = super().get_context_data(**kwargs)

        get_age = self.kwargs['age']
        context['f'] = 'f'

        if get_age == 0:
            start_age = 4
            last_age = 99
        elif get_age == 1:
            start_age = 4
            last_age = 17
        elif get_age == 2:
            start_age = 18
            last_age = 34

        elif get_age == 3:
            start_age = 35
            last_age = 49

        elif get_age == 4:
            start_age = 50
            last_age = 99

        if get_age == 0:
            context['tot_dist'] = Statistic.objects.filter(runner_stat__not_running=False).filter(
                runner_stat__runner_gender='ж').values('runner_stat__username', 'runner_stat__runner_team',
                                                       'total_runs', 'total_time', 'runner_stat__runner_gender',
                                                       'runner_stat__runner_gender', 'runner_stat__runner_group',
                                                       'total_balls', 'total_balls_for_champ','total_days', 'total_distance',
                                                       'total_average_temp').order_by('-total_balls')
            return context






        else:
            context['tot_dist'] = Statistic.objects.filter(
                runner_stat__runner_age__gte=start_age). \
                filter(runner_stat__runner_age__lte=last_age).filter(runner_stat__runner_gender='ж').filter(
                runner_stat__not_running=False).values('runner_stat__username', 'runner_stat__runner_team',
                                                       'runner_stat__runner_gender', 'runner_stat__runner_group',
                                                       'total_runs', 'total_time', 'runner_stat__runner_gender',
                                                       'total_balls', 'total_balls_for_champ', 'total_days',
                                                       'total_distance',
                                                       'total_average_temp').order_by('-total_balls')
            return context


class RunnersView(DataMixin, ListView):
    model = User
    template_name = 'runners.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.kwargs:
            cat_selected = self.kwargs['cat']
            context['cat_selected'] = cat_selected
            if cat_selected != 'f':
                context['profile'] = get_user_model().objects.filter(runner_category=cat_selected,
                                                                     not_running=False).values('username',
                                                                                               'runner_category',
                                                                                               'runner_age',
                                                                                               'runner_gender',
                                                                                               'runner_group__group_title')
                context['count_of_runners'] = get_user_model().objects.filter(runner_category=cat_selected,
                                                                              not_running=False).count()

            else:
                context['profile'] = get_user_model().objects.filter(runner_gender='ж', not_running=False).values(
                    'username',
                    'runner_category',
                    'runner_age',
                    'runner_gender',
                    'runner_group__group_title')

            return context



        else:
            context['count_of_runners'] = get_user_model().objects.all().count()
            context['profile'] = get_user_model().objects.all().filter(not_running=False).values('username',
                                                                                                 'runner_category',
                                                                                                 'runner_age',
                                                                                                 'runner_gender',
                                                                                                 'runner_group__group_title')
            return context


class Tables(DataMixin, ListView):
    model = Teams
    template_name = 'tables.html'

    def get_queryset(self):
        return Teams.objects.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        context['count_of_teams'] = Teams.objects.all().count()

        # context['runner'] = RunnerDay.objects.filter(runner__user__username=self.kwargs['runner']).order_by(
        #     'day_select')
        # result = RunnerDay.objects.filter(runner__user__username=self.kwargs['runner']). \
        #     values('runner__user_id', 'runner__user__username'). \
        #     annotate(total_dist=Sum('day_distance'), total_time=Sum('day_time'),
        #              avg_time=Avg('day_average_temp')).order_by('-total_dist')
        #
        # context['data'] = get_user_model().objects.filter(user__username=self.kwargs['runner'])
        #
        # context['tot_dist'] = result
        return context


# просмотр списка команд с количеством участников на странице КОМАНДЫ
class ComandsView(DataMixin, ListView):
    model = Teams
    template_name = 'tables.html'
    context_object_name = 'comand'

    def get_queryset(self):
        return Teams.objects.all()

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        teams = Teams.objects.values_list('team', flat=True)

        qs = dict()
        for team in teams:
            # q=Statistic.objects.filter(tota)
            best5 = Statistic.objects.filter(runner_stat__runner_team=team).annotate(total_dist=Sum('total_distance'),
                                                                                     total_times=Sum('total_time'),
                                                                                     total_average_temps=Sum(
                                                                                         'total_average_temp'),
                                                                                     total_ball=Sum('total_balls'),
                                                                                     statistic_total_runs=Sum(
                                                                                         'total_runs'),
                                                                                     avg_time=ExpressionWrapper(
                                                                                         F('total_average_temps') / F(
                                                                                             'statistic_total_runs'),
                                                                                         output_field=TimeField())).order_by(
                '-total_ball'). \
                aggregate(Sum('total_dist'), Sum('total_times'), Avg('avg_time'), Sum('total_ball'))

            qs[team] = best5

        new_list = []
        my_list = []
        for k, v in qs.items():
            new_list.append(k)
            new_list.append(v['total_dist__sum']) if v['total_dist__sum'] is not None else new_list.append(0)
            new_list.append(v['total_ball__sum']) if v['total_ball__sum'] is not None else new_list.append(0)
            # new_list.append(v['total_dist__sum'])
            new_list.append(v['total_times__sum']) if v['total_times__sum'] is not None else new_list.append(0)
            # new_list.append(v['avg_time__avg'])
            new_list.append(v['avg_time__avg']) if v['avg_time__avg'] is not None else new_list.append(0)

        for i in range(0, len(new_list), 5):
            my_list.append(new_list[i:i + 5])

        list_of_lists = list(sorted(my_list, key=lambda x: x[1], reverse=True))

        my_dict = {}
        for item in list_of_lists:
            my_dict[item[0]] = {
                'total_dist__sum': item[1],
                'total_times__sum': item[2],
                'avg_time__avg': item[3],
                'total_ball__sum': item[4],

                'count_runners': get_user_model().objects.filter(runner_team__team=item[0]).count()
            }
            # my_dict[item[0]]['count_runners']= get_user_model().objects.filter(runner_team_id=item[0]).count()

        context['qs'] = my_dict
        context['comset'] = teams

        context['number_runner'] = get_user_model().objects.filter(not_running=False).values('username').order_by(
            'username')
        # def get_context_data(self, *, object_list=None, **kwargs):
        #     context = super().get_context_data(**kwargs)

        #
        #     c = Teams.objects.all()
        #     runner_list = get_user_model().objects.all().order_by('runner_team')
        #     context['runset'] = set(runner_list)
        #
        #     com_list = {}
        #
        #     for x in c:
        #         num_of_runners = get_user_model().objects.filter(runner_team=x.team).count()
        #         com_list[x] = num_of_runners
        #
        #
        #     context['comset'] = com_list
        #
        #     runers_count = get_user_model().objects.filter(id__gt=1).filter(not_running=False).values('username')
        #
        #     # runer = get_user_model().objects.get('username')
        #
        #     context['number_runner'] = get_user_model().objects.filter(id__gt=1).filter(not_running=False).values('username').order_by(
        #         'username')

        # result = RunnerDay.objects.filter(runner__user__username=self.kwargs['runner']). \
        #     values('runner__user_id', 'runner__user__username'). \
        #     annotate(total_dist=Sum('day_distance'), total_time=Sum('day_time'),
        #              avg_time=Avg('day_average_temp')).order_by('-total_dist')
        #
        # context['data'] = get_user_model().objects.filter(user__username=self.kwargs['runner'])

        # context['tot_dist'] = result
        return context


class OneTeamStat(DataMixin, ListView):
    model = User
    template_name = 'comanda.html'
    context_object_name = 'comand'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        comand_number = self.kwargs['comanda']
        context['comand_number'] = comand_number
        users = get_user_model().objects.filter(runner_team__team=comand_number)
        context['team_count'] = users.count()
        user_stats = Statistic.objects.filter(runner_stat__in=users)
        # Общая статистика группы
        context['res'] = user_stats.aggregate(
            tot_time=Sum('total_time'),
            tot_balls=Sum('total_balls'),
            tot_avg_temp=Sum('total_average_temp'),
            tot_distance=Sum('total_distance'),
            tot_runs=Sum('total_runs'),
            day_count=Sum('total_days'),
            avg_time=Avg('total_average_temp'))

        # статистика каждого участника
        context['qs'] = Statistic.objects.filter(
            runner_stat__runner_team__team=comand_number). \
            values('runner_stat__username', 'runner_stat__runner_category',
                   'runner_stat__runner_age', 'runner_stat__runner_gender',
                   'total_time', 'total_distance', 'total_days', 'total_runs', 'total_balls',
                   'total_average_temp').order_by('-total_balls')
        return context


#
# вывод общей статистики по командам без учета категорий (просто общий пробег время)
# на странице РЕЗУЛЬТАТЫ КОМАНД
# TODO здесь переделать команды
# class ComandsRes(DataMixin, ListView):
#     model = User
#     template_name = 'total.html'
#     context_object_name = 'comand'
#
#     def get_queryset(self):
#         return Teams.objects.all()
#
#     def get_total_sum(self):
#         return RunnerDay.objects.filter(runner__runner_team=F('runner__runner_team')). \
#             annotate(  # отсеиваем средний темп меньше 7
#             total_dist=Sum('day_distance'), total_time=Sum('day_time'),
#             avg_time=Sum('day_average_temp'), total_ball=Sum('ball')). \
#             values('runner__runner_team', 'runner__runner_category', 'total_dist', 'total_time',
#                    'avg_time', 'total_ball').order_by('-total_ball')
#
#     def get_context_data(self, *args, object_list=None, **kwargs):
#         context = super().get_context_data(**kwargs)

#
#         teams = Teams.objects.values_list('team', flat=True)
#
#         qs = dict()
#         for team in teams:
#             best5 = RunnerDay.objects.filter(runner__runner_team__team=team) \
#                 .values(
#                 'runner__user__username', 'runner__runner_category').annotate(total_dist=Sum('day_distance'),
#                                                                               total_time=Sum('day_time'),
#                                                                               total_average_temp=Sum(
#                                                                                   'day_average_temp'),
#                                                                               total_ball=Sum('ball'),
#                                                                               avg_time=ExpressionWrapper(
#                                                                                   F('total_average_temp') / F(
#                                                                                       'runner__statistic_total_runs'),
#                                                                                   output_field=TimeField()).order_by(
#                                                                                   '-total_ball')). \
#                 aggregate(Sum('total_dist'), Sum('total_time'), Avg('avg_time'), Sum('total_ball'))
#
#             qs[team] = best5
#
#         new_list = []
#         my_list = []
#         for k, v in qs.items():
#             new_list.append(k)
#             new_list.append(v['total_dist__sum']) if v['total_dist__sum'] is not None else new_list.append(0)
#             new_list.append(v['total_ball__sum']) if v['total_ball__sum'] is not None else new_list.append(0)
#             # new_list.append(v['total_dist__sum'])
#             new_list.append(v['total_time__sum']) if v['total_time__sum'] is not None else new_list.append(0)
#             # new_list.append(v['avg_time__avg'])
#             new_list.append(v['avg_time__avg']) if v['avg_time__avg'] is not None else new_list.append(0)
#
#         for i in range(0, len(new_list), 5):
#             my_list.append(new_list[i:i + 5])
#
#         list_of_lists = list(sorted(my_list, key=lambda x: x[1], reverse=True))
#
#         my_dict = {}
#         for item in list_of_lists:
#             my_dict[item[0]] = {
#                 'total_dist__sum': item[1],
#                 'total_time__sum': item[2],
#                 'avg_time__avg': item[3],
#                 'total_ball__sum': item[4],
#
#                 'count_runners': get_user_model().objects.filter(runner_team__team=item[0]).count()
#             }
#             # my_dict[item[0]]['count_runners']= get_user_model().objects.filter(runner_team_id=item[0]).count()
#
#         context['qs'] = my_dict
#         context['comset'] = teams
#
#         context['number_runner'] = get_user_model().objects.filter(not_running=False).values('username').order_by(
#             'username')
#
#         return context

class Championate(DataMixin, ListView):
    model = User
    template_name = 'championat.html'
    context_object_name = 'best_runners'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        teams = Teams.objects.values_list('team', flat=True)

        data = []
        for team in teams:
            team_stats = Statistic.objects.filter(
                runner_stat__runner_team__team=team,
                runner_stat__not_running=False
            ).order_by('-total_balls_for_champ')

            age18 = team_stats.filter(runner_stat__runner_age__lte=17).order_by('-total_balls_for_champ')[:5]
            age35 = team_stats.filter(runner_stat__runner_age__gte=18, runner_stat__runner_age__lte=35).order_by('-total_balls_for_champ')[:5]
            age49 = team_stats.filter(runner_stat__runner_age__gt=35, runner_stat__runner_age__lte=49).order_by('-total_balls_for_champ')[:5]
            ageover50 = team_stats.filter(runner_stat__runner_age__gt=49).order_by('-total_balls_for_champ')[:5]

            # Используем get для получения значения с защитой от None
            age18_sum = sum(x.total_balls_for_champ or 0 for x in age18)
            age35_sum = sum(x.total_balls_for_champ or 0 for x in age35)
            age49_sum = sum(x.total_balls_for_champ or 0 for x in age49)
            ageover50_sum = sum(x.total_balls_for_champ or 0 for x in ageover50)

            total_balls_for_champ = age18_sum + age35_sum + age49_sum + ageover50_sum

            data.append({
                'team': team,
                'total_balls_for_champ': total_balls_for_champ,
                'age18': age18_sum,
                'age35': age35_sum,
                'age49': age49_sum,
                'ageover50': ageover50_sum,
            })

        data.sort(key=lambda x: x['total_balls_for_champ'], reverse=True)

        context['qs'] = data

        return context




    # def get_queryset(self):

    # return Statistic.objects.annotate(
    #     age_group=Cast('runner_stat__runner_age', output_field=models.IntegerField())
    # ).filter(runner_stat__isnull=False).annotate(
    #     team=Cast('runner_stat__runner_team', output_field=models.IntegerField())
    # ).values('age_group', 'team', 'runner_stat').annotate(
    #     total_balls=Sum('total_balls')
    # ).order_by('-total_balls').annotate(
    #     rank=Window(expression=RowNumber(), order_by=[-F('total_balls')])
    # ).values('age_group', 'team', 'runner_stat', 'total_balls', 'rank').order_by('age_group', 'team', 'rank')[:5]
    # def get_queryset(self):
    #     age_categories = [
    #         ('cat1', 5, 17),  # Age group 5-17
    #         ('cat2', 18, 35),  # Age group 18-35
    #         ('cat3', 36, 49),  # Age group 36-49
    #         ('cat4', 50, 99)  # Age group 50+
    #     ]

    #     team_results = {}

    #     # Iterate over each age category
    #     for category_name, age_start, age_end in age_categories:
    #         # Get all statistics for runners in this age range
    #         filtered_stats = Statistic.objects.filter(
    #             runner_stat__runner_age__gte=age_start,
    #             runner_stat__runner_age__lte=age_end
    #         )

    #         # Rank runners based on total balls scored for championship
    #         ranked_stats = filtered_stats.annotate(
    #             rank=Window(
    #                 expression=RowNumber(),
    #                 order_by=F('total_balls_for_champ').desc()
    #             )
    #         )

    #         # Get top five participants in this category
    #         top_five_stats = ranked_stats.filter(rank__lte=5)

    #         # Calculate total balls scored by these top five participants per team
    #         team_totals = top_five_stats.values('runner_stat__runner_team').annotate(
    #             total_balls_sum=Sum('total_balls_for_champ')
    #         )

    #         # Store results by team number (assuming 'team' is a field in User model)
    #         for team_total in team_totals:
    #             team = team_total['runner_stat__runner_team']  # Replace with actual field if different
    #             total_balls_sum = team_total['total_balls_sum'] or 0

    #             if team not in team_results:
    #                 team_results[team] = {
    #                     'team_number': team,
    #                     'results': {category_name: total_balls_sum},
    #                     'total_sum': total_balls_sum  # Initialize total sum with current category's sum
    #                 }
    #             else:
    #                 team_results[team]['results'][category_name] = total_balls_sum
    #                 team_results[team]['total_sum'] += total_balls_sum  # Add to the overall total sum

    #     # Ensure all teams are represented even if they have no participants in some categories
    #     all_teams = User.objects.values('runner_team__team').distinct()  # Assuming 'team' is a field in User model

    #     for team in all_teams:
    #         team_number = team['runner_team__team']
    #         if team_number not in team_results:
    #             team_results[team_number] = {
    #                 'team_number': team_number,
    #                 'results': {cat[0]: 0 for cat in age_categories},  # Initialize all categories to zero
    #                 'total_sum': 0  # Initialize total sum to zero
    #             }

    #     # Convert results into a list and sort by total sum in descending order
    #     sorted_results = sorted(
    #         [{'team_number': result['team_number'], 'results': result['results'], 'total_sum': result['total_sum']}
    #          for result in team_results.values()],
    #         key=lambda x: x['total_sum'],
    #         reverse=True
    #     )

    #     return sorted_results

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     return context

    # def get_context_data(self, *args, object_list=None, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #
    #     try:
    #         context['qs'] = Championat.objects.all().values_list('team_id__team', 'balls', 'age18', 'age35', 'age49',
    #                                                              'ageover50').order_by('-balls')
    #     except:
    #         context['qs'] = []
    #
    #     return context

    #     return context

    # team_scores = Statistic.objects.annotate(
    #     age_group=F('runner_stat__runner_age')// 18 ,
    #
    #     adjusted_points=Coalesce(F('total_balls'), Value(0)) - 1,
    # ).values('runner_stat__runner_team', 'age_group').order_by('runner_stat__runner_team', '-adjusted_points')[:5].annotate(
    #     total_points=Sum('adjusted_points')
    # ).order_by('runner_stat__runner_team', 'age_group').annotate(
    #     total_points=Sum('total_points'))
    #
    # # Now, let's aggregate the scores for each team and age group
    # team_aggregated_scores = team_scores.values('runner_stat__runner_team', 'age_group').annotate(
    #     total_points=Sum('adjusted_points')
    # ).order_by('runner_stat__runner_team', 'age_group')
    #
    # # Finally, we can calculate the total scores for each team across all age groups
    # total_scores = team_aggregated_scores.values('runner_stat__runner_team').annotate(
    #     total_points=Sum('total_points')
    # )
    # print(team_scores)
    #
    #
    #
    # queryset = Statistic.objects.values('runner_stat__runner_team', 'runner_stat__runner_age').annotate(
    #     under_18_points=Coalesce(Sum('total_balls', filter=Q(runner_stat__runner_age__lt=18)), Value(0)),
    #     age_18_to_35_points=Coalesce(
    #         Sum('total_balls', filter=Q(runner_stat__runner_age__gte=18, runner_stat__runner_age__lt=36)),
    #         Value(0)),
    #     age_36_to_49_points=Coalesce(
    #         Sum('total_balls', filter=Q(runner_stat__runner_age__gte=36, runner_stat__runner_age__lt=50)),
    #         Value(0)),
    #     above_49_points=Coalesce(Sum('total_balls', filter=Q(runner_stat__runner_age__gte=50)), Value(0)),
    #     total_points=Sum('total_balls')
    # ).order_by('runner_stat__runner_team')

    # TODO запрос работает но будет жрать много ресурсов

    #
    #
    # for team in teams:
    #     total_run_sum = 0
    #     my_list.append(team)
    #     #
    #     # best18runners = Statistic.objects.filter(runner_stat__runner_team=team).filter(total_distance__gt=0). \
    #     #                     filter(runner_stat__not_running=False).filter(runner_stat__runner_age__lte=17). \
    #     #                     order_by('-total_balls')[:4].annotate(total_ball=Sum('total_balls')).aggregate(
    #     #     Sum('total_ball'))
    #
    #     # best18runners = Statistic.objects.filter(runner_stat__runner_team=team).filter(total_distance__gt=0). \
    #     #                     filter(runner_stat__not_running=False).filter(runner_stat__runner_age__lte=17). \
    #     #                     order_by('-total_balls')[:4]
    #     # print(best18runners)
    #     # best34runners = Statistic.objects.filter(runner_stat__runner_team=team).filter(total_distance__gt=0). \
    #     #                     filter(runner_stat__not_running=False).filter(runner_stat__runner_age__gte=18).filter(
    #     #     runner_stat__runner_age__lte=34).order_by('-total_balls')[:4].annotate(
    #     #     total_ball=Sum('total_balls')).aggregate(Sum('total_ball'))
    #     best34runners = Statistic.objects.filter(runner_stat__runner_team=team).filter(total_distance__gt=0). \
    #                         filter(runner_stat__not_running=False).filter(runner_stat__runner_age__gte=18).filter(
    #         runner_stat__runner_age__lte=34).order_by('-total_balls')[:5]
    #
    #     print(best34runners)
    #     # best49runners = Statistic.objects.filter(runner_stat__runner_team=team).filter(total_distance__gt=0). \
    #     #                     filter(runner_stat__not_running=False).filter(runner_stat__runner_age__gte=35).filter(
    #     #     runner_stat__runner_age__lte=49).order_by('-total_balls')[:4].annotate(
    #     #     total_ball=Sum('total_balls')).aggregate(Sum('total_ball'))
    #     # print(best49runners)
    #     # best50runners = Statistic.objects.filter(runner_stat__runner_team=team).filter(total_distance__gt=0). \
    #     #                     filter(runner_stat__not_running=False).filter(runner_stat__runner_age__gte=50).order_by(
    #     #     '-total_balls')[:4].annotate(
    #     #     total_ball=Sum('total_balls')).aggregate(Sum('total_ball'))
    #     #
    #     # print(best50runners)
    #
    #     for i in range(1, 4):
    #         best1cat = Statistic.objects.filter(runner_stat__runner_team=team).filter(
    #             runner_stat__runner_category=i). \
    #                        filter(total_distance__gt=0).values(
    #             'runner_stat__username', 'runner_stat__runner_category').annotate(total_ball=Sum('total_balls')) \
    #                        .order_by('-total_ball')[:4].aggregate(Sum('total_ball'))
    #
    #         my_list.append(i)
    #
    #         if best1cat['total_ball__sum'] == None:
    #             my_list.append(0)
    #         else:
    #             my_list.append(best1cat['total_ball__sum'])
    #             total_run_sum += best1cat['total_ball__sum']
    #
    #     my_list.append('total_ball_sum')
    #     my_list.append(total_run_sum)
    # #
    # new_list = []
    #
    # for i in range(0, len(my_list), 9):
    #     new_list.append(my_list[i:i + 9])
    #
    # list_of_lists = sorted(new_list, key=lambda x: x[8], reverse=True)
    #
    # for item in list_of_lists:
    #     my_dict[item[0]] = {
    #         'cat1': item[2],
    #         'cat2': item[4],
    #         'cat3': item[6],
    #         'total_run_sum': item[8]
    #     }
    #
    # context['qs'] = my_dict
    #
    # return context


from django.utils import translation
from django.utils.translation import gettext as _


class StatisticView(DataMixin, ListView):
    model = User
    template_name = 'statistic.html'
    context_object_name = 'data'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Статистика")
        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        return RunnerDay.objects.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        context['total_registered'] = get_user_model().objects.filter(not_running=False).count()
        context['total_runners'] = get_user_model().objects.filter(not_running=False).count()
        context['runners_mens'] = get_user_model().objects.filter(runner_gender='м', not_running=False).count()
        context['runners_womens'] = get_user_model().objects.filter(runner_gender='ж', not_running=False).count()

        # context['runner_age_1'] = get_user_model().objects.filter(runner_age__lte=17, not_running=False).count()
        # context['runner_age_2'] = get_user_model().objects.filter(runner_age__gte=18, runner_age__lte=35, not_running=False).count()
        # context['runner_age_3'] = get_user_model().objects.filter(runner_age__gte=36,  runner_age__lte=49, not_running=False).count()
        # context['runner_age_4'] = get_user_model().objects.filter(runner_age__gte=50, not_running=False).count()

        context['run2022'] = get_user_model().objects.filter(zabeg22=True, not_running=False).count()
        context['run2023'] = get_user_model().objects.filter(zabeg23=True, not_running=False).count()
        context['total_distance'] = Statistic.objects.all().aggregate(Sum('total_distance'))['total_distance__sum']
        context['total_time'] = Statistic.objects.all().aggregate(Sum('total_time'))['total_time__sum']
        context['total_runs'] = Statistic.objects.all().aggregate(Sum('total_runs'))['total_runs__sum']
        # context['age_before_18'] = get_user_model().objects.filter(runner_age__lte=17, not_running=False).count()
        # context['age_21_30'] = get_user_model().objects.filter(runner_age__gte=18, runner_age__lte=35, not_running=False).count()
        # context['age_31_40'] = get_user_model().objects.filter(runner_age__gte=18, runner_age__lte=35, not_running=False).count()
        # context['age_41_50'] = get_user_model().objects.filter(runner_age__gte=36,  runner_age__lte=49, not_running=False).count()
        # context['age_over_50'] = get_user_model().objects.filter(runner_age__gte=50, not_running=False).count(
        # context['run30'] = RunnerDay.objects.annotate(day_count=Count(
        #     (Q(day_average_temp__lte="00:08:00") & Q(
        #         day_distance__gt=0)) |
        #     (Q(day_average_temp__gte='00:08:00') & Q(
        #         runner__runner_age__gte=60)))).count()
        count_cat_list = {}
        i = 1
        # num_of_runners = 0
        # for j in [400, 200, 100, 50, 20]:
        #     count_cat = RunnerDay.objects.filter(runner__runner_category=i). \
        #         filter((Q(day_average_temp__lte="00:08:00") & Q(day_distance__gt=0)) |
        #                (Q(day_average_temp__gte='00:08:00') & Q(runner_age__gte=60))).values(
        #         'username').annotate(total_dist=Sum('day_distance'), total_time=Sum('day_time'),
        #                              total_average_temp=Sum('day_average_temp')).filter(
        #         total_dist__gte=j).count()
        #     count_cat_list[i] = count_cat
        #     num_of_runners += count_cat
        #     i += 1
        #     if i > 5:
        #         break

        context['get_finished'] = count_cat_list

        context['disqauled'] = Statistic.objects.filter(total_distance__lt=30).count()

        have_run = Statistic.objects.filter(total_distance__gt=0).count()

        context['not_run'] = context['total_runners'] - have_run
        count_of_run_every_day = []
        distance_every_day = []
        for x in range(1, 31):
            count_of_run_every_day.append(RunnerDay.objects.filter(day_select=x).count())
            if RunnerDay.objects.filter(day_select=x, day_distance__gt=0).aggregate(Sum('day_distance'))[
                'day_distance__sum'] == None:
                distance_every_day.append(0)
            else:
                distance_every_day.append(
                    RunnerDay.objects.filter(day_select=x).aggregate(Sum('day_distance'))['day_distance__sum'])
        context['count_of_run_every_day'] = count_of_run_every_day
        context['distance_every_day'] = distance_every_day

        # context['count_of_ages'] = Statistic.objects.aggregate(
        #     under_20=Count('id', filter=Q(runner_stat__runner_age__lte=20)),
        #     age_21_30=Count('id', filter=Q(runner_stat__runner_age__gt=21, runner_stat__runner_age__lte=30)),
        #     age_31_40=Count('id', filter=Q(runner_stat__runner_age__gt=30, runner_stat__runner_age__lte=40)),
        #     age_41_50=Count('id', filter=Q(runner_stat__runner_age__gt=40, runner_stat__runner_age__lte=50)),
        #     age_over_50=Count('id', filter=Q(runner_stat__runner_age__gt=50)))

        context['count_of_ages'] = get_user_model().objects.aggregate(
            under_18=Count('id', filter=Q(runner_age__lte=17, not_running=False)),
            age_18_35=Count('id', filter=Q(runner_age__gt=17, runner_age__lte=35, not_running=False)),
            age_36_49=Count('id', filter=Q(runner_age__gt=35, runner_age__lte=49, not_running=False)),
            age_over_50=Count('id', filter=Q(runner_age__gt=49, not_running=False)))

        # context['get_finished_1'] = RunnerDay.objects.filter(runner__runner_category=1). \
        #     filter((Q(day_average_temp__lte="00:08:00") & Q(day_distance__gt=0)) |
        #            (Q(day_average_temp__gte='00:08:00') & Q(runner__runner_age__gte=60))).values(
        #     'runner__user__username').annotate(total_dist=Sum('day_distance'), total_time=Sum('day_time'),
        #                                        total_average_temp=Sum('day_average_temp')).filter(total_dist__gte=400).count()
        #
        # context['get_finished_2'] = RunnerDay.objects.filter(runner__runner_category=2). \
        #     filter((Q(day_average_temp__lte="00:08:00") & Q(day_distance__gt=0)) |
        #            (Q(day_average_temp__gte='00:08:00') & Q(runner__runner_age__gte=60))).values(
        #     'runner__user__username').annotate(total_dist=Sum('day_distance'), total_time=Sum('day_time'),
        #                                        total_average_temp=Sum('day_average_temp')).filter(total_dist__gte=200).count()
        #
        # context['get_finished_3'] = RunnerDay.objects.filter(runner__runner_category=3). \
        #     filter((Q(day_average_temp__lte="00:08:00") & Q(day_distance__gt=0)) |
        #            (Q(day_average_temp__gte='00:08:00') & Q(runner__runner_age__gte=60))).values(
        #     'runner__user__username').annotate(total_dist=Sum('day_distance'), total_time=Sum('day_time'),
        #                                        total_average_temp=Sum('day_average_temp')).filter(total_dist__gte=100).count()
        #
        # context['get_finished_4'] = RunnerDay.objects.filter(runner__runner_category=4). \
        #     filter((Q(day_average_temp__lte="00:08:00") & Q(day_distance__gt=0)) |
        #            (Q(day_average_temp__gte='00:08:00') & Q(runner__runner_age__gte=60))).values(
        #     'runner__user__username').annotate(total_dist=Sum('day_distance'), total_time=Sum('day_time'),
        #                                        total_average_temp=Sum('day_average_temp')).filter(total_dist__gte=50).count()
        #
        # context['get_finished_5'] = RunnerDay.objects.filter(runner__runner_category=5). \
        #     filter((Q(day_average_temp__lte="00:08:00") & Q(day_distance__gt=0)) |
        #            (Q(day_average_temp__gte='00:08:00') & Q(runner__runner_age__gte=60))).values(
        #     'runner__user__username').annotate(total_dist=Sum('day_distance'), total_time=Sum('day_time'),
        #                                        total_average_temp=Sum('day_average_temp')).filter(
        #     total_dist__gte=50).count()

        context['runners_cat1'] = get_user_model().objects.filter(runner_category=1, not_running=False).count()
        context['runners_cat2'] = get_user_model().objects.filter(runner_category=2, not_running=False).count()
        context['runners_cat3'] = get_user_model().objects.filter(runner_category=3, not_running=False).count()

        return context


# отображение групп с участниками

# def group_list(request):
#     groups = Group.objects.all()
#     #
#     # group_users = {}
#     # for group in groups:
#     #
#     #     members = Statistic.objects.filter(runner_stat__runner_group=group)
#     #
#     #     mygroup = get_user_model().objects.filter(runner_group=group)
#     #
#     #     group_users[group] = []
#     #     for user in mygroup:
#     #
#     #         try:
#     #             user_stat = Statistic.objects.get(runner_stat_id=user.id)
#     #
#     #             group_users[group].append({
#     #                 'group': group.group_title,
#     #                 'user': user.username,
#     #                 'total_distance': user_stat.total_distance,
#     #                 'total_time': user_stat.total_time,
#     #                 'total_average_temp': user_stat.total_average_temp,
#     #                 'total_days': user_stat.total_days,
#     #                 'total_runs': user_stat.total_runs,
#     #                 'total_balls': user_stat.total_balls,
#     #                 'is_qualificated': user_stat.is_qualificated
#     #             })
#     #             print(group_users[group])
#     #         except IntegrityError:
#     #             pass
#
#     return render(request, 'groups.html', {'groups': groups, 'group_users': group_users})


# def group_statistics_view(request):
#     if 'groups' in request.path_info:
#         groups = GroupsResult.objects.all().order_by('-group_total_distance')
#         flag = True
#
#     else:
#         groups = ComandsResult.objects.all().order_by('-comand_total_distance')
#         flag = False

def group_statistics_view(request):
    groups = Group.objects.all()
    teams = Teams.objects.all()

    if 'groups' in request.path_info:
        statistics = []
        for group in groups:
            statistics_group = Statistic.objects.filter(runner_stat__runner_group=group.id,
                                                        runner_stat__not_running=False, total_balls__gt=0)

            total_distance = statistics_group.aggregate(total_distance=Sum('total_distance'))['total_distance']
            total_balls_for_champ = statistics_group.aggregate(total_balls_for_champ=Sum('total_balls_for_champ'))['total_balls_for_champ']
            total_balls = statistics_group.aggregate(total_balls=Sum('total_balls'))['total_balls']
            total_time = statistics_group.aggregate(total_time=Sum('total_time'))['total_time']
            total_average_temp = statistics_group.aggregate(total_average_temp=Avg('total_average_temp'))['total_average_temp']

            participants = []
            for statistic in statistics_group:
                participants.append({
                    'username': statistic.runner_stat.username,
                    'total_distance': statistic.total_distance,
                    'total_balls': statistic.total_balls,
                    'total_balls_for_champ': statistic.total_balls_for_champ,
                    'total_time': statistic.total_time,
                    'total_average_temp': statistic.total_average_temp
                })

            statistics.append({
                'title': group.group_title,
                'group_id': group.id,
                'total_distance': total_distance,
                'total_balls': total_balls,
                'total_time': total_time,
                'total_balls_for_champ': total_balls_for_champ,
                'total_average_temp': total_average_temp,
                'participants': participants
            })
        statistics = sorted(statistics, key=lambda x: x['total_balls'] or 0, reverse=True)
        context = {
            'statistics': statistics,
            'flag': True
        }
    else:
        statistics = []
        for team in teams:
            statistics_team = Statistic.objects.filter(runner_stat__runner_team=team.id,runner_stat__not_running=False,
                                                       total_balls__gt=0)

            total_distance = statistics_team.aggregate(total_distance=Sum('total_distance'))['total_distance']
            total_balls = statistics_team.aggregate(total_balls=Sum('total_balls'))['total_balls']
            total_balls_for_champ = statistics_team.aggregate(total_balls_for_champ=Sum('total_balls_for_champ'))['total_balls_for_champ']
            total_time = statistics_team.aggregate(total_time=Sum('total_time'))['total_time']
            total_average_temp = statistics_team.aggregate(total_average_temp=Avg('total_average_temp'))['total_average_temp']

            participants = []
            for statistic in statistics_team:
                participants.append({
                    'username': statistic.runner_stat.username,
                    'total_distance': statistic.total_distance,
                    'total_balls_for_champ': statistic.total_balls_for_champ,
                    'total_balls': statistic.total_balls,
                    'total_time': statistic.total_time,
                    'total_average_temp': statistic.total_average_temp
                })

            statistics.append({
                'title': team.team,

                'total_distance': total_distance,
                'total_balls': total_balls,
                'total_balls_for_champ': total_balls_for_champ,
                'total_time': total_time,
                'total_average_temp': total_average_temp,
                'participants': participants
            })
        statistics = sorted(statistics, key=lambda x: x['total_balls'] or 0, reverse=True)
        context = {
            'statistics': statistics,
            'flag': False
        }

    return render(request, 'allgroups.html', context)

def runner_day_results_view(request, day):
    results = RunnerDay.objects.filter(day_select=day, runner__not_running=False, day_distance__gt=0).order_by(
        '-ball', '-day_distance')
    return render(request, 'runner_day_results.html', {'results': results, 'day': day})


def exportcsv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'

    writer = csv.writer(response, delimiter=";")
    writer.writerow(['uchastnik', 'day', 'ball', 'number_of_run', 'distance', 'time', 'average'])

    users = RunnerDay.objects.all().values_list('runner__username', 'day_select', 'ball', 'number_of_run',
                                                'day_distance', 'day_time',
                                                'day_average_temp')
    for user in users:
        writer.writerow(user)

    return response


def faq(request):
    return render(request, 'faq.html')


def page_not_found_view(request, exception):
    return render(request, '404.html', status=404)
