from django.db.models import Count

from core.models import User


class DataMixin:

    # def __init__(self):
    #     self.request = None

    def get_user_context(self, **kwargs):
        context = kwargs
        cats = User.objects.annotate(Count('runner_category'))
        context['count_of_runners'] = User.objects.all().count() + 1
        # user_menu = menu.copy()
        context['calend'] = {x: x for x in range(1, 31)}
        # if not self.request.user.is_authenticated:
        #     user_menu.pop(1)

        # context['menu'] = user_menu

        context['cats'] = cats
        if 'cat_selected' not in context:
            context['cat_selected'] = 0
        return context


