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

admin.site.register(KeyWordClass, KeyWordAdmin)
