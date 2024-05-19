from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager

from django.contrib.auth.models import User, AbstractUser, PermissionsMixin
from django.db import models

from django.utils.translation import gettext_lazy as _


class Teams(models.Model):
    class Meta:
        verbose_name = 'команда'
        verbose_name_plural = "команды"

    rangeteam = range(100, 236)
    TEAM = [(i, i) for i in rangeteam]

    team = models.PositiveIntegerField(verbose_name='команда', unique=True, choices=TEAM, default=100)

    def __str__(self):
        return str(self.team)


class KeyWordClass(models.Model):
    kwteam=models.ForeignKey(Teams, on_delete=models.CASCADE, verbose_name='команда')
    keyword= models.CharField(verbose_name='кодовое слово')

    def __str__(self):
        return str(self.keyword)

    class Meta:
        verbose_name = "Ключевые слова"
        verbose_name_plural= "Ключевые слова"


class CustomUserManager(BaseUserManager):
    def _create_user(self, username=None, password=None, **extra_fields):
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        return self._create_user(username, password, **extra_fields)


class Family(models.Model):
    runner = models.ForeignKey('CustomUser', on_delete=models.DO_NOTHING, verbose_name='Участник')
    runner_family = models.ManyToManyField(to='CustomUser',blank=True, related_name='runners_family')

    class Meta:
        verbose_name = 'Семейное участие'
        verbose_name_plural = 'Семейное участие'

    def __str__(self):
        return str(self.runner)

class CustomUser(AbstractUser):
    GENDER = [
        ('м', "м"), ("ж", "ж")
    ]
    CATEGORY = [
        (1, 'Новичок'), (2, 'Любитель'), (3, 'Профи')
    ]
    CATEGORY_WOMEN = [
        (1, 'Новичок'), (2, 'Любитель')
    ]
    email = False
    # user= models.CharField( max_length=12,verbose_name='Номер участника', unique=True)
    # runner_team = models.ForeignKey(Teams, on_delete=models.DO_NOTHING, verbose_name='команда', db_index=True)
    runner_team = models.PositiveIntegerField(verbose_name='команда', db_index=True)
    runner_age = models.PositiveIntegerField(verbose_name='возраст', db_index=True)
    runner_category = models.PositiveIntegerField(verbose_name='Заявляетесь в группу', choices=CATEGORY, default=1,
                                                  db_index=True)
    runner_gender = models.CharField(max_length=1, choices=GENDER, verbose_name='пол участника', default='м')
    zabeg22 = models.BooleanField(verbose_name='Участник МыZaБег 2022', default=False)
    zabeg23 = models.BooleanField(verbose_name='Участник МыZaБег 2023', default=False)
    # family = models.ManyToManyField(to=User, verbose_name='выберите участников',
    #                                 related_name='family_users', blank=True)

    # category_updated = models.PositiveIntegerField(verbose_name='Начальная группа', choices=CATEGORY, blank=True,
    #                                                null=True)
    # completed = models.BooleanField(default=False, verbose_name="Выполнена квал-я", )

    REQUIRED_FIELDS = ['runner_team', 'runner_age', 'runner_category', 'runner_gender', 'zabeg22', 'zabeg23']
    objects = CustomUserManager()

    class Meta:
        verbose_name = 'участник'
        verbose_name_plural = "участники"

    def __str__(self):
        return str(self.username)

    def _value(self):
        if self.runner_gender == 'м':
            return u'%s' % self.CATEGORY

        else:
            return u'%s' % self.CATEGORY_WOMEN

    value = property(_value)

