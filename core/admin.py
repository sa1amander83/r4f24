from django.contrib import admin

# Register your models here.
from unittest import runner

from django.contrib import admin

# Register your models here.
from django.contrib.admin import display

from core.models import User, Teams, Family, KeyWordClass


class TeamsAdmin(admin.ModelAdmin):
    search_fields = ('team',)
    list_display = ('team',)
    list_display_links = ('team',)

    list_filter = ('team',)
    ordering = ('team',)
    list_per_page = 50
    list_max_show_all = 100


class RunnerAdmin(admin.ModelAdmin):
    # resource_class = TeamsAdmin
    # def пробег_за_день(self, username, day_distance=None):
    #     result = RunnerDay.objects.filter(user__user__username=username).filter(
    #         user__runnerday__day_distance=day_distance)
    #
    #     return result
    #
    # def дистанция_за_день(self, username):
    #     result = RunnerDay.objects.filter(user__user__username=username)
    #     return result
    #
    # def время_пробега(self, username):
    #     result = RunnerDay.objects.filter(user__user__username=username)
    #     return result
    #
    # def средний_темп(self, username):
    #     result = RunnerDay.objects.filter(user__user__username=username)
    #     return result

    # fields = ('пробег_за_день', 'дистанция_за_день', 'время_пробега', 'средний_темп',)
    search_fields = (
        'username', 'runner_team__team', 'runner_age', 'runner_category', 'runner_gender', 'zabeg22')
    list_editable = ('runner_age', 'runner_category', 'runner_gender', 'zabeg22', 'zabeg23')
    list_display = ('username', 'runner_team', 'runner_age', 'runner_category', 'runner_gender', 'zabeg22', 'zabeg23')
    # 'пробег_за_день','дистанция_за_день', 'время_пробега', 'средний_темп',)
    # list_display = ('user', 'runner_age', 'runner_category', 'runner_gender', 'zabeg22', )
    list_display_links = ('username', 'runner_team',)

    # list_filter = ('runner_category','category_updated','completed', 'is_admin', 'runner_team',)
    ordering = ('username',)

    list_per_page = 50
    list_max_show_all = 50


class UsersInline(admin.TabularInline):
    model = Family.runner_family.through
    # model=Family
    extra = 1


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    class Meta:
        verbose_name = 'Семья'

    def __str__(self):
        return str(self.username)

    inlines = (UsersInline,)
    list_display = ["runner"]

    filter_horizontal = ('runner_family',)


class KeyWordAdmin(admin.ModelAdmin):
    list_display = ('kwteam', 'keyword',)
    ordering = ('kwteam',)


admin.site.register(Teams, TeamsAdmin)
admin.site.register(User, RunnerAdmin)
admin.site.register(KeyWordClass, KeyWordAdmin)
