from django.db import models
from django.contrib.auth.models import User
from django.db.models.aggregates import Count
from random import randint
from datetime import datetime, timedelta, time
from django.utils import timezone

from django.utils.timezone import now as django_datetime_now


class RandomManager(models.Manager):
    def random(self, test_id):
        answer = None
        while answer == None:
            count = self.aggregate(count=Count('id'))['count']
            random_index = randint(0, count - 1)
            try:
                answer = self.all().filter(test_id=test_id)[random_index]
            except Exception as e:
                pass
        print(answer)
        return answer


class predmet(models.Model):
    predmet_name = models.CharField('Название предмета', max_length=256, default=None, unique=True)
    predmet_name_sokr = models.CharField('Название предмета сокращенно', max_length=20, default=None, unique=True)
    predmet_name_sokr_translite = models.CharField('Название предмета сокращенно англ', max_length=30, default=None,
                                                   blank=True, unique=True)

    def save(self, *args, **kwargs):
        def translit(text):
            cyrillic = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
            latin = 'a|b|v|g|d|e|e|zh|z|i|i|k|l|m|n|o|p|r|s|t|u|f|kh|tc|ch|sh|shch||y||e|iu|ia'.split('|')
            trantab = {k: v for k, v in zip(cyrillic, latin)}
            newtext = ''
            for ch in text:
                casefunc = str.capitalize if ch.isupper() else str.lower
                newtext += casefunc(trantab.get(ch.lower(), ch))
            return newtext

        self.predmet_name_sokr = self.predmet_name_sokr.upper()
        self.predmet_name_sokr_translite = translit(self.predmet_name_sokr).upper()
        super(predmet, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предметы'
        db_table = 'predmet'

    def __str__(self):
        return self.predmet_name_sokr


class test(models.Model):
    test_name = models.CharField('Название теста', max_length=50, default=None)
    valid_date = models.DateField('Дата действия теста', default=None)
    predmet_id = models.ForeignKey(predmet, on_delete=models.CASCADE, verbose_name='Предмет', default=None)
    create_user_id = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Создатель теста')
    voprosi_count = models.PositiveSmallIntegerField('Число вопросов', default=0, blank=True)
    decision_time = models.TimeField('Время на решение теста', default='01:00:00', blank=True)
    active_status = models.BooleanField('Статус публикации', default=False, blank=True)

    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'
        db_table = 'test'

    def __str__(self):
        return self.test_name


class voprosi(models.Model):
    vopros = models.TextField('Вопрос', default=None)
    otvet = models.CharField('Ответ', max_length=256, default=None)
    test_id = models.ForeignKey(test, on_delete=models.CASCADE, verbose_name='Тест')

    objects = RandomManager()

    def save(self, *args, **kwargs):
        self.otvet = self.otvet.lower()
        super(voprosi, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        db_table = 'voprosi'

    def __str__(self):
        return self.vopros + ' ' + self.otvet


class test_for_user(models.Model):
    test_id = models.ForeignKey(test, on_delete=models.CASCADE, verbose_name='Тест')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    start_time = models.DateTimeField('Время создания теста', blank=True, default=django_datetime_now)
    end_time = models.DateTimeField('Время завершения теста', default=None, blank=True, null=True)
    ocenka = models.PositiveSmallIntegerField('Оценка', default=0, blank=True)
    end_status = models.BooleanField('Решен/Не решен', default=False, blank=True, null=True)
    override_status = models.BooleanField('Разрешено ли перерешать тест', default=False, blank=True, null=True)

    class Meta:
        verbose_name = 'Тест пользователя'
        verbose_name_plural = 'Тесты пользователей'
        db_table = 'test_for_user'

    def __str__(self):
        return f'{self.test_id} - {self.user_id} - {self.ocenka}'


class test_for_user_voprosi(models.Model):
    test_for_user_id = models.ForeignKey(test_for_user, on_delete=models.CASCADE, verbose_name='Тест пользователя')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    voprosi_id = models.ForeignKey(voprosi, on_delete=models.CASCADE, verbose_name='Вопрос')
    voprose_num = models.PositiveSmallIntegerField('Номер вопроса', default=0, blank=True)
    otvet_user = models.CharField('Ответ пользователя', max_length=256, default=None, null=True, blank=True)
    otvet_status = models.BooleanField('Правильно/Не правильно', default=False, blank=True, null=True)

    class Meta:
        verbose_name = 'Ответ пользователя'
        verbose_name_plural = 'Ответы пользователей'
        db_table = 'test_for_user_voprosi'

    def save(self, *args, **kwargs):
        try:
            self.otvet_user = self.otvet_user.lower()
        except:
            pass
        super(test_for_user_voprosi, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.otvet_user} - {self.otvet_status}'

# class user_data(models.Model):
#     last_name = models.CharField('Фамилия', max_length=50, default=None)
#     first_name = models.CharField('Имя', max_length=50, default=None)
#     patronymic = models.CharField('Отчество', max_length=50, default=None)
#     password = models.CharField('Пароль', max_length=50, default=None)
#     email = models.EmailField('Email', default=None, unique=True)
#     user_name = models.CharField('Логин', max_length=50, default=None, unique=True)
#     id_users_lvl = models.ForeignKey('prototipe.users_lvl', on_delete=models.CASCADE, verbose_name='Роль')
#
#     class Meta:
#         verbose_name = 'Пользователя'
#         verbose_name_plural = 'Пользователи'
#         db_table = 'user_data'
#
#
# class users_lvl(models.Model):
#     lvl_name = models.CharField('Роль', max_length=50, default=None)
#
#     def __str__(self):
#         return self.lvl_name
#
#     class Meta:
#         verbose_name = 'Роль'
#         verbose_name_plural = 'Роли'
#         db_table = 'users_lvl'
#
# class auth_token(models.Model):
#     token = models.CharField('Token', max_length=256, default=None)
#     id_user = models.ForeignKey('prototipe.user_data', on_delete=models.CASCADE, verbose_name='Пользователь')
#
#     def __str__(self):
#         return self.token
#
#     class Meta:
#         verbose_name = 'Сессия'
#         verbose_name_plural = 'Сессии'
#         db_table = 'auth_token'
