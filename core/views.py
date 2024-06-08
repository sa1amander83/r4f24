from django.db.models import Q, Sum, Count, ExpressionWrapper, TimeField, F, Avg
from django.views.generic import ListView
from core.models import User, Teams
from profiles.models import RunnerDay, Statistic, RunnerDay
from profiles.utils import DataMixin


class IndexView(DataMixin, ListView):
    model = Statistic
    template_name = 'index.html'
    context_object_name = 'stat'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['calend'] = {x: x for x in range(1, 31)}
        # cats=list('Новичок','Легкий','Средний', 'Тяжелый', 'Ультра' )

        # context['userid'] = Statistic.objects.filter(runner_id__gte=0)
        context['user_detail'] = User.objects.filter(id=self.request.user.id)
        context['cat_selected'] = 0
        context['age'] = 0
        context['count_of_runners'] = User.objects.exclude(not_running=True).count()

        # result = RunnerDay.objects.filter(id__gte=1).values('runner__user_id', 'runner__user__username'). \
        #     annotate(total_dist=Sum('day_distance'), total_time=Sum('day_time'),
        #              avg_time=Avg('day_average_temp')).order_by('-total_dist')

        # result = RunnerDay.objects.filter(id__gte=1). \
        #     filter((Q(day_average_temp__lte="00:08:00") & Q(day_distance__gt=0)) |
        #            (Q(day_average_temp__gte='00:08:00') & Q(runner__runner_age__gte=60))).values(
        #     'runner__user__username', 'runner__runner_category').annotate(total_dist=Sum('day_distance'),
        #                                                                   total_time=Sum('day_time'),
        #                                                                   total_average_temp=Sum('day_average_temp'),
        #                                                                   day_count=Count(
        #                                                                       (Q(day_average_temp__lte="00:08:00") & Q(
        #                                                                           day_distance__gt=0)) |
        #                                                                       (Q(day_average_temp__gte='00:08:00') & Q(
        #                                                                           runner__runner_age__gte=60))),
        #                                                                   avg_time=ExpressionWrapper(
        #                                                                       F('total_average_temp') / F('day_count'),
        #                                                                       output_field=TimeField())). \
        #     order_by('-total_dist')

        context['tot_dist'] = Statistic.objects.filter(runner_stat__not_running=False).order_by('-total_balls')

        return context

    # def get_queryset(self):
    #     return RunnerDay.objects.all()


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
            all_runners = User.objects.all()

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

            # values('runner__runner_team', 'total_dist', 'total_time',
            #        'avg_time').


class RunnersCatView(DataMixin, ListView):
    model = RunnerDay
    template_name = 'category.html'
    context_object_name = 'stat'

    def get_context_data(self, *, object_list=None, **kwargs):
        global start_age, last_age
        context = super().get_context_data(**kwargs)
        cat_selected = self.kwargs['cat']
        # context['calend'] = {x: x for x in range(1, 31)}
        get_age = self.kwargs['age']
        get_gender = self.kwargs['gender']
        if cat_selected == 'all':
            context['all'] = User.objects.filter(not_running=False)
        if get_gender == 'm':
            gender = 'м'

        elif get_gender == 'f':
            gender = 'ж'

        else:
            gender = 'all'

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

        if cat_selected == 0 and get_age == 0 and gender == 'all':
            context['tot_dist'] = User.objects.filter(not_running=False)

        elif cat_selected == 0 and get_age == 0 and get_gender == 'f':
            context['tot_dist'] = User.objects.filter(not_running=False).filter(runner_gender='ж')


        elif cat_selected != 0 and get_age != 0 and gender != 'all':
            context['tot_dist'] = User.objects.filter(runner_category=cat_selected).filter(runner_age__gte=start_age). \
                filter(runner_age__lte=last_age).filter(runner_gender=gender).filter(not_running=False)

        elif cat_selected != 0 and gender != 'all':
            context['tot_dist'] = User.objects.filter(runner_category=cat_selected).filter(runner_age__gte=start_age). \
                filter(runner_age__lte=last_age).filter(runner_gender=gender).filter(not_running=False)

        elif cat_selected == 0 and gender == 'all':
            context['tot_dist'] = User.objects.filter(runner_category=cat_selected).filter(runner_age__gte=start_age). \
                filter(runner_age__lte=last_age).filter(runner_gender=gender).filter(not_running=False)




        elif gender == 'all' and get_age != 0 and cat_selected != 0:
            context['tot_dist'] = User.objects.filter(runner_category=cat_selected). \
                filter(not_running=False).filter(runner_age__gte=start_age). \
                filter(runner_age__lte=last_age)

        elif cat_selected == 0 and gender == 'all':
            context['tot_dist'] = User.objects.filter(runner_category=cat_selected).filter(not_running=False)

        else:
            context['tot_dist'] = User.objects.filter(runner_category=cat_selected).filter(runner_age__gte=start_age). \
                filter(runner_age__lte=last_age).filter(not_running=False)

        #
        # context['userid'] = Statistic.objects.filter(runner_id__gte=0)
        # context['user_detail'] = User.objects.filter(id=self.request.user.id)
        context['cat_selected'] = cat_selected

        # if cat_selected == 'woman':
        #     result = RunnerDay.objects.filter(id__gte=1).filter(runner__runner_gender='ж').values('runner__user_id',
        #                                                                                           'runner__runner_category',
        #                                                                                           'runner__user__username'). \
        #         annotate(total_dist=Sum('day_distance'), total_time=Sum('day_time'),
        #                  avg_time=Avg('day_average_temp')).order_by('-total_dist')
        #
        #
        # elif cat_selected == '50':
        #     result = RunnerDay.objects.filter(id__gte=1).filter(runner__runner_age__gte=50).values('runner__user_id',
        #                                                                                            'runner__runner_category',
        #                                                                                            'runner__user__username'). \
        #         annotate(total_dist=Sum('day_distance'), total_time=Sum('day_time'),
        #                  avg_time=Avg('day_average_temp')).order_by('-total_dist')
        #
        #
        #
        # else:
        #     result = RunnerDay.objects.filter(id__gte=1).filter(runner__runner_category=cat_selected).values(
        #         'runner__user_id', 'runner__user__username', 'runner__runner_category'). \
        #         annotate(total_dist=Sum('day_distance'), total_time=Sum('day_time'),
        #                  avg_time=Avg('day_average_temp')).order_by('-total_dist')
        #
        # context['tot_dist'] = result

        return context

    def get_queryset(self):
        return RunnerDay.objects.all()


class RunnersView(DataMixin, ListView):
    model = User
    template_name = 'runners.html'

    # def user(self):
    #     return RunnerDay.objects.get(pk=self.pk)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['calend'] = {x: x for x in range(1, 31)}

        if self.kwargs:
            cat_selected = self.kwargs['cat']
            context['cat_selected'] = cat_selected

            if cat_selected == '0':
                context['profile'] = User.objects.filter(not_running=False).values('username',
                                                                                   'runner_category', 'runner_age',
                                                                                   'runner_gender')
                context['count_of_runners'] = User.objects.filter(not_running=False).count()
                return context
            elif cat_selected == 5:
                context['profile'] = User.objects.filter(runner_gender='ж').values('username',
                                                                                   'runner_category',
                                                                                   'runner_age',
                                                                                   'runner_gender')
                context['count_of_runners'] = User.objects.filter(runner_gender='ж').count()

                return context

            elif cat_selected == '50':

                context['profile'] = User.objects.filter(runner_age__gte=50).values('username',
                                                                                    'runner_category',
                                                                                    'runner_age',
                                                                                    'runner_gender')
                context['count_of_runners'] = User.objects.filter(runner_age__gte=50).count()
                return context
            elif int(cat_selected) > 0 and int(cat_selected) < 6:
                context['profile'] = User.objects.filter(runner_category=cat_selected).values('username',
                                                                                              'runner_category',
                                                                                              'runner_age',
                                                                                              'runner_gender')
                context['count_of_runners'] = User.objects.filter(runner_category=cat_selected).count()
                return context



        else:
            context['count_of_runners'] = User.objects.all().count()
            context['profile'] = User.objects.all().filter(not_running=False).values('username', 'runner_category',
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
        # context['data'] = User.objects.filter(user__username=self.kwargs['runner'])
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

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['calend'] = {x: x for x in range(1, 31)}

        c = Teams.objects.all()
        runner_list = User.objects.all().order_by('runner_team')
        context['runset'] = set(runner_list)

        com_list = {}

        for x in c:
            num_of_runners = User.objects.filter(runner_team=x.team).count()
            com_list[x] = num_of_runners
        context['comset'] = com_list

        runers_count = User.objects.filter(id__gt=1).filter(not_running=False).values('username')

        # runer = User.objects.get('username')

        context['number_runner'] = User.objects.filter(id__gt=1).filter(not_running=False).values('username').order_by(
            'username')

        # result = RunnerDay.objects.filter(runner__user__username=self.kwargs['runner']). \
        #     values('runner__user_id', 'runner__user__username'). \
        #     annotate(total_dist=Sum('day_distance'), total_time=Sum('day_time'),
        #              avg_time=Avg('day_average_temp')).order_by('-total_dist')
        #
        # context['data'] = User.objects.filter(user__username=self.kwargs['runner'])

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

        team_count = RunnerDay.objects.filter(runner__runner_team__team=comand_number).count()
        # context['res'] = RunnerDay.objects.filter(runner__runner_team__team=comand_number).filter(Q(
        #     day_average_temp__lte="00:08:00") & Q(day_distance__gt=0)).values(
        #     'runner__user__username'). \
        #     annotate(total_dist=Sum('day_distance'), total_time=Sum('day_time'),
        #              avg_time=Avg('day_average_temp')).aggregate(Sum('total_dist'), Sum('total_time'), Avg('avg_time'))

        context['res'] = RunnerDay.objects.filter(runner__runner_team__team=comand_number). \
            filter((Q(day_average_temp__lte="00:08:00") & Q(day_distance__gt=0)) |
                   (Q(day_average_temp__gte='00:08:00') & Q(runner__runner_age__gte=60))).values(
            'runner__user__username', 'runner__runner_category').annotate(total_dist=Sum('day_distance'),
                                                                          total_time=Sum('day_time'),
                                                                          total_average_temp=Sum('day_average_temp'),
                                                                          day_count=Count(
                                                                              (Q(day_average_temp__lte="00:08:00") & Q(
                                                                                  day_distance__gt=0)) |
                                                                              (Q(day_average_temp__gte='00:08:00') & Q(
                                                                                  runner__runner_age__gte=60))),
                                                                          avg_time=ExpressionWrapper(
                                                                              F('total_average_temp') / F('day_count'),
                                                                              output_field=TimeField())). \
            aggregate(Sum('total_dist'), Sum('total_time'), Avg('avg_time'))

        result = RunnerDay.objects.filter(runner__runner_team__team=comand_number). \
            filter((Q(day_average_temp__lte="00:08:00") & Q(day_distance__gt=0)) |
                   (Q(day_average_temp__gte='00:08:00') & Q(runner__runner_age__gte=60))).values(
            'runner__user__username', 'runner__runner_category').annotate(total_dist=Sum('day_distance'),
                                                                          total_time=Sum('day_time'),
                                                                          total_average_temp=Sum('day_average_temp'),
                                                                          day_count=Count(
                                                                              (Q(day_average_temp__lte="00:08:00") & Q(
                                                                                  day_distance__gt=0)) |
                                                                              (Q(day_average_temp__gte='00:08:00') & Q(
                                                                                  runner__runner_age__gte=60))),
                                                                          avg_time=ExpressionWrapper(
                                                                              F('total_average_temp') / F('day_count'),
                                                                              output_field=TimeField()),
                                                                          avg_team_time=ExpressionWrapper(
                                                                              F('avg_time') / team_count,
                                                                              output_field=TimeField()),

                                                                          ). \
            order_by('-total_dist')
        context['tot_dist'] = result

        number_runner = User.objects.filter(user__username__startswith=comand_number) \
            .values('username', 'runner_category', 'runner_age', 'runner_gender').order_by('username')

        qs = list()
        for i in result:
            user = list(i.values())[0]

            try:
                for j in number_runner:

                    user2 = list(j.values())[0]

                    if user == user2:
                        qs.append({**j, **i})

            except:
                continue

        context['qs'] = qs

        return context


#
# вывод общей статистики по командам без учета категорий (просто общий пробег время)
# на странице РЕЗУЛЬТАТЫ КОМАНД

class ComandsResults(DataMixin, ListView):
    model = User
    template_name = 'total.html'
    context_object_name = 'comand'

    def get_queryset(self):
        return Teams.objects.all()

    def get_total_sum(self):
        return RunnerDay.objects.filter(runner__runner_team=F('runner__runner_team')).filter(day_average_temp__lte=7). \
            annotate(  # отсеиваем средний темп меньше 7
            total_dist=Sum('day_distance'), total_time=Sum('day_time'),
            avg_time=Sum('day_average_temp')). \
            values('runner__runner_team', 'runner__runner_category', 'total_dist', 'total_time',
                   'avg_time').order_by('-total_dist')

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['calend'] = {x: x for x in range(1, 31)}

        teams = Teams.objects.values_list('team', flat=True)

        qs = dict()
        for team in teams:
            best5 = RunnerDay.objects.filter(runner__runner_team__team=team). \
                filter((Q(day_average_temp__lte="00:08:00") & Q(day_distance__gt=0)) |
                       (Q(day_average_temp__gte='00:08:00') & Q(runner__runner_age__gte=60))).values(
                'runner__user__username', 'runner__runner_category').annotate(total_dist=Sum('day_distance'),
                                                                              total_time=Sum('day_time'),
                                                                              total_average_temp=Sum(
                                                                                  'day_average_temp'),
                                                                              day_count=Count(
                                                                                  (
                                                                                          Q(day_average_temp__lte="00:08:00") & Q(
                                                                                      day_distance__gt=0)) |
                                                                                  (
                                                                                          Q(day_average_temp__gte='00:08:00') & Q(
                                                                                      runner__runner_age__gte=60))),
                                                                              avg_time=ExpressionWrapper(
                                                                                  F('total_average_temp') / F(
                                                                                      'day_count'),
                                                                                  output_field=TimeField())). \
                aggregate(Sum('total_dist'), Sum('total_time'), Avg('avg_time'))

            qs[team] = best5

        new_list = []
        my_list = []
        for k, v in qs.items():
            new_list.append(k)
            new_list.append(v['total_dist__sum']) if v['total_dist__sum'] != None else new_list.append(0)
            # new_list.append(v['total_dist__sum'])
            new_list.append(v['total_time__sum']) if v['total_time__sum'] != None else new_list.append(0)
            # new_list.append(v['avg_time__avg'])
            new_list.append(v['avg_time__avg']) if v['avg_time__avg'] != None else new_list.append(0)

        for i in range(0, len(new_list), 4):
            my_list.append(new_list[i:i + 4])

        list_of_lists = list(sorted(my_list, key=lambda x: x[1], reverse=True))

        my_dict = {}
        for item in list_of_lists:
            my_dict[item[0]] = {
                'total_dist__sum': item[1],
                'total_time__sum': item[2],
                'avg_time__avg': item[3],
                'count_runners': User.objects.filter(runner_team__team=item[0]).count()
            }
            # my_dict[item[0]]['count_runners']= User.objects.filter(runner_team_id=item[0]).count()

        context['qs'] = my_dict
        context['comset'] = teams

        context['number_runner'] = User.objects.filter(user_id__gt=1).values('username').order_by(
            'username')

        return context


class Championat(DataMixin, ListView):
    model = User
    template_name = 'championat.html'
    context_object_name = 'champ'

    def get_context_data(self, *args, object_list=None, **kwargs):
        teams = Teams.objects.values_list('team', flat=True)
        my_list = []
        my_dict = {}

        context = super().get_context_data(**kwargs)
        context['calend'] = {x: x for x in range(1, 31)}
        # TODO переделать расчет
        # for team in teams:
        #     total_run_sum = 0
        #     my_list.append(team)
        #     for i in range(1, 4):
        #         best1cat = RunnerDay.objects.filter(runner__runner_team=team).filter(runner__runner_category=i). \
        #                        filter((Q(day_average_temp__lte="00:08:00") & Q(day_distance__gt=0)) |
        #                               (Q(day_average_temp__gte='00:08:00') & Q(runner__runner_age__gte=60))).values(
        #             'runner__username', 'runner__runner_category').annotate(total_dist=Sum('day_distance')) \
        #                        .order_by('-total_dist')[:4].aggregate(Sum('total_dist'))
        #
        #         my_list.append(i)
        #
        #         if best1cat['total_dist__sum'] == None:
        #             my_list.append(0)
        #         else:
        #             my_list.append(best1cat['total_dist__sum'])
        #             total_run_sum += best1cat['total_dist__sum']
        #
        #     my_list.append('total_run_sum')
        #     my_list.append(total_run_sum)
        #
        # new_list = []

        # for i in range(0, len(my_list), 13):
        #     new_list.append(my_list[i:i + 13])
        #
        # list_of_lists = sorted(new_list, key=lambda x: x[12], reverse=True)
        #
        # for item in list_of_lists:
        #     my_dict[item[0]] = {
        #         'cat1': item[2],
        #         'cat2': item[4],
        #         'cat3': item[6],
        #         'cat4': item[8],
        #         'cat5': item[10],
        #         'total_run_sum': item[12]
        #     }

        # context['qs'] = my_dict

        return context


class StatisticView(DataMixin, ListView):
    model = User
    template_name = 'statistic.html'
    context_object_name = 'data'

    def get_queryset(self):
        return RunnerDay.objects.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['calend'] = {x: x for x in range(1, 31)}

        context['total_runners'] = User.objects.all().filter(not_running=False).count()
        context['runners_mens'] = User.objects.filter(runner_gender='м').count()
        context['runners_womens'] = User.objects.filter(runner_gender='ж').count()

        context['runner_age_1'] = User.objects.filter(runner_age__lte=25).count()
        context['runner_age_2'] = User.objects.filter(runner_age__gte=26).filter(runner_age__lte=30).count()
        context['runner_age_3'] = User.objects.filter(runner_age__gte=31).filter(runner_age__lte=35).count()
        context['runner_age_4'] = User.objects.filter(runner_age__gte=36).filter(runner_age__lte=40).count()

        context['run2022'] = User.objects.filter(zabeg22=True).count()
        context['run2023'] = User.objects.filter(zabeg23=True).count()
        context['run30'] = RunnerDay.objects.filter(runner_id__gte=1).annotate(day_count=Count(
            (Q(day_average_temp__lte="00:08:00") & Q(
                day_distance__gt=0)) |
            (Q(day_average_temp__gte='00:08:00') & Q(
                runner__runner_age__gte=60)))).count()
        count_cat_list = {}
        i = 1
        num_of_runners = 0
        for j in [400, 200, 100, 50, 20]:
            count_cat = RunnerDay.objects.filter(runner_category=i). \
                filter((Q(day_average_temp__lte="00:08:00") & Q(day_distance__gt=0)) |
                       (Q(day_average_temp__gte='00:08:00') & Q(runner_age__gte=60))).values(
                'username').annotate(total_dist=Sum('day_distance'), total_time=Sum('day_time'),
                                     total_average_temp=Sum('day_average_temp')).filter(
                total_dist__gte=j).count()
            count_cat_list[i] = count_cat
            num_of_runners += count_cat
            i += 1
            if i > 5:
                break

        context['get_finished'] = count_cat_list

        context['disqauled'] = context['total_runners'] - num_of_runners

        have_run = RunnerDay.objects.filter((Q(day_average_temp__lte="00:08:00") & Q(day_distance__gt=0)) |
                                            (Q(day_average_temp__gte='00:08:00') & Q(
                                                runner_age__gte=60))).values(
            'runner__user__username').annotate(total_dist=Sum('day_distance'), total_time=Sum('day_time'),
                                               total_average_temp=Sum('day_average_temp')).count()

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

        context['runners_cat1'] = User.objects.filter(runner_category=1).count()
        context['runners_cat2'] = User.objects.filter(runner_category=2).count()
        context['runners_cat3'] = User.objects.filter(runner_category=3).count()

        return context
