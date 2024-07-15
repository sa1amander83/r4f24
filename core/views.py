import csv

from django.contrib.auth import get_user_model
from django.db import models, IntegrityError
from django.db.models import Q, Sum, Count, ExpressionWrapper, TimeField, F, Avg, Window

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
        context['tot_dist'] = Statistic.objects.filter(runner_stat__not_running=False).\
        values('runner_stat__username','total_time','total_distance','runner_stat__runner_gender','runner_stat__runner_category',
                                                                                              'total_runs','total_balls','total_average_temp').order_by('-total_balls', '-total_distance')

        return context


class CatListView(DataMixin, ListView):
    model = User
    template_name = 'total.html'
    context_object_name = 'comand'

    def get_queryset(self):
        return Teams.objects.all()

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['calend'] = {x: x for x in range(1, 31)}

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

        context['tot_dist'] = Statistic.objects.filter(runner_stat__not_running=False).values(
            'runner_stat__username', 'runner_stat__runner_team', 'total_runs', 'total_time',
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

        if cat_selected != 0:
            context['tot_dist'] = Statistic.objects.filter(runner_stat__runner_category=cat_selected).filter(
                runner_stat__runner_age__gte=start_age). \
                filter(runner_stat__runner_age__lte=last_age).filter(
                runner_stat__not_running=False).values('runner_stat__username', 'runner_stat__runner_team',
                                                       'total_runs', 'total_time',
                                                       'total_balls', 'total_days', 'total_distance',
                                                       'total_average_temp').order_by('-total_balls')

            return context
        else:
            context['tot_dist'] = Statistic.objects.filter(
                runner_stat__runner_age__gte=start_age). \
                filter(runner_stat__runner_age__lte=last_age).filter(
                runner_stat__not_running=False).values('runner_stat__username', 'runner_stat__runner_team',
                                                       'total_runs', 'total_time',
                                                       'total_balls', 'total_days', 'total_distance',
                                                       'total_average_temp').order_by('-total_balls')

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
                                                       'total_runs', 'total_time',
                                                       'total_balls', 'total_days', 'total_distance',
                                                       'total_average_temp').order_by('-total_balls')
            return context


        else:
            context['tot_dist'] = Statistic.objects.filter(
                runner_stat__runner_age__gte=start_age). \
                filter(runner_stat__runner_age__lte=last_age).filter(runner_stat__runner_gender='ж').filter(
                runner_stat__not_running=False).values('runner_stat__username', 'runner_stat__runner_team',
                                                       'total_runs', 'total_time',
                                                       'total_balls', 'total_days', 'total_distance',
                                                       'total_average_temp').order_by('-total_balls')
            return context


class RunnersView(DataMixin, ListView):
    model = User
    template_name = 'runners.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['calend'] = {x: x for x in range(1, 31)}

        if self.kwargs:
            cat_selected = self.kwargs['cat']
            context['cat_selected'] = cat_selected
            if cat_selected != 'f':
                context['profile'] = get_user_model().objects.filter(runner_category=cat_selected).values('username',
                                                                                                          'runner_category',
                                                                                                          'runner_age',
                                                                                                          'runner_gender')
                context['count_of_runners'] = get_user_model().objects.filter(runner_category=cat_selected).count()

            else:
                context['profile'] = get_user_model().objects.filter(runner_gender='ж').values('username',
                                                                                               'runner_category',
                                                                                               'runner_age',
                                                                                               'runner_gender')

            return context



        else:
            context['count_of_runners'] = get_user_model().objects.all().count()
            context['profile'] = get_user_model().objects.all().filter(not_running=False).values('username',
                                                                                                 'runner_category',
                                                                                                 'runner_age',
                                                                                                 'runner_gender')
            return context


class Tables(DataMixin, ListView):
    model = Teams
    template_name = 'tables.html'

    def get_queryset(self):
        return Teams.objects.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['calend'] = {x: x for x in range(1, 31)}

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
        context['calend'] = {x: x for x in range(1, 31)}

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
        #     context['calend'] = {x: x for x in range(1, 31)}
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
        context['calend'] = {x: x for x in range(1, 31)}

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
                   'runner_stat__runner_age',
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
#         context['calend'] = {x: x for x in range(1, 31)}
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

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['calend'] = {x: x for x in range(1, 31)}
        try:
            context['qs'] = Championat.objects.all().values_list('team_id__team', 'balls', 'age18', 'age35', 'age49',
                                                                 'ageover50').order_by('-balls')
        except:
            context['qs'] = []
        return context

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


class StatisticView(DataMixin, ListView):
    model = User
    template_name = 'statistic.html'
    context_object_name = 'data'

    def get_queryset(self):
        return RunnerDay.objects.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['calend'] = {x: x for x in range(1, 31)}

        context['total_runners'] = get_user_model().objects.all().filter(not_running=False).count()
        context['runners_mens'] = get_user_model().objects.filter(runner_gender='м').filter(not_running=False).count()
        context['runners_womens'] = get_user_model().objects.filter(runner_gender='ж').filter(not_running=False).count()

        context['runner_age_1'] = get_user_model().objects.filter(runner_age__lte=17).filter(not_running=False).count()
        context['runner_age_2'] = get_user_model().objects.filter(runner_age__gte=18).filter(not_running=False).filter(
            runner_age__lte=35).count()
        context['runner_age_3'] = get_user_model().objects.filter(runner_age__gte=36).filter(not_running=False).filter(
            runner_age__lte=49).count()
        context['runner_age_4'] = get_user_model().objects.filter(runner_age__gte=50).filter(not_running=False).count()

        context['run2022'] = get_user_model().objects.filter(zabeg22=True).filter(not_running=False).count()
        context['run2023'] = get_user_model().objects.filter(zabeg23=True).filter(not_running=False).count()
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

        context['runners_cat1'] = get_user_model().objects.filter(runner_category=1).filter(not_running=False).count()
        context['runners_cat2'] = get_user_model().objects.filter(runner_category=2).filter(not_running=False).count()
        context['runners_cat3'] = get_user_model().objects.filter(runner_category=3).filter(not_running=False).count()

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


def group_statistics_view(request):
    if 'groups' in request.path_info:
        groups = GroupsResult.objects.all().order_by('-group_total_balls')
        flag = True

    else:
        groups = ComandsResult.objects.all().order_by('-comand_total_balls')
        flag = False

    # group_data = {}

    # for group in groups:
    #
    #     if 'groups' in request.path_info:
    #         users = get_user_model().objects.filter(runner_group=group)
    #
    #     else:
    #         users = get_user_model().objects.filter(runner_team=group)
    #
    #     user_stats = Statistic.objects.filter(runner_stat__in=users)
    #
    #     total_results = user_stats.aggregate(
    #
    #         total_balls=Sum('total_balls'),
    #         total_distance=Sum('total_distance'),
    #         total_time=Sum('total_time'),
    #         total_average_temp=Avg('total_average_temp'),
    #         total_days=Sum('total_days'),
    #         total_runs=Sum('total_runs'),
    #         tot_users=Count('runner_stat__username')
    #     )
    #
    #     group_data[group] = {
    #         'users': users,
    #         'total_results': total_results,
    #         'user_stats': user_stats
    #     }

    context = {
        'group_data': groups, 'flag': flag,
    }
    return render(request, 'allgroups.html', context)


def runner_day_results_view(request, day):
    results = RunnerDay.objects.filter(day_select=day)
    return render(request, 'runner_day_results.html', {'results': results, 'day': day})


def exportcsv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'

    writer = csv.writer(response, delimiter=";")
    writer.writerow(['uchastnik', 'day', 'ball', 'number_of_run', 'distance', 'time', 'average'])

    users = RunnerDay.objects.all().values_list('runner__username', 'day_select','ball' ,'number_of_run', 'day_distance', 'day_time',
                                                'day_average_temp')
    for user in users:
        writer.writerow(user)

    return response

