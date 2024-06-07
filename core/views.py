from django.db.models import Q, Sum, Count, ExpressionWrapper, TimeField, F, Avg
from django.views.generic import ListView
from core.models import User, Teams
from profiles.models import RunnerDay, Statistic
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

        # print( context['count_of_runners'])
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

        # print(result[1]['avg_time'])

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

        if cat_selected == 5:
            gender = 'ж'
        else:
            gender = 'м'
            # context['tot_dist'] = Statistic.objects.filter(runner_stat__runner_gender='ж').\
            #     filter(runner_stat__not_running=False)
        print(cat_selected)
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

        if  cat_selected==0:
            context['tot_dist'] = User.objects.filter(not_running=False)
        else:
            context['tot_dist'] = User.objects.filter(runner_category=cat_selected).filter(runner_age__gte=start_age).\
            filter(runner_age__lte=last_age).filter(runner_gender=gender)


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
