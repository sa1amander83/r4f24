from django.db.models import Q, Sum, Count, ExpressionWrapper, TimeField, F
from django.views.generic import ListView
from core.models import User
from profiles.models import RunnerDay
from profiles.utils import DataMixin


class IndexView(DataMixin, ListView):
    model = RunnerDay
    template_name = 'index.html'
    context_object_name = 'stat'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['calend'] = {x: x for x in range(1, 31)}
        # cats=list('Новичок','Легкий','Средний', 'Тяжелый', 'Ультра' )

        # context['userid'] = Statistic.objects.filter(runner_id__gte=0)
        context['user_detail'] = User.objects.filter(id=self.request.user.id)

        context['count_of_runners'] = User.objects.all().count()

        # print( context['count_of_runners'])
        # result = RunnerDay.objects.filter(id__gte=1).values('runner__user_id', 'runner__user__username'). \
        #     annotate(total_dist=Sum('day_distance'), total_time=Sum('day_time'),
        #              avg_time=Avg('day_average_temp')).order_by('-total_dist')

        result = RunnerDay.objects.filter(id__gte=1). \
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
            order_by('-total_dist')

        # print(result[1]['avg_time'])

        context['tot_dist'] = result

        return context

    # def get_queryset(self):
    #     return RunnerDay.objects.all()
