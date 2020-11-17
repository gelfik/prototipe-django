from django.db import models
from django.contrib.auth.models import User
from django.db.models.aggregates import Count
from django.utils.translation import gettext_lazy as _
from random import randint

from datetime import datetime, timedelta, time
from django.utils import timezone

from django.utils.timezone import now as django_datetime_now


class Test_Status_List(models.TextChoices):
    Created = '0', _('Создание')
    Review = '1', _('Отправлен на проверку')
    ReCreated = '2', _('Не прошел проверку, внесите правки')
    Published = '3', _('Опубликован')
    Deleted = '4', _('Удален')


class RandomManager_voprosi(models.Manager):
    def random(self, test_id):
        answer = None
        while answer == None:
            count = self.aggregate(count=Count('id'))['count']
            random_index = randint(0, count - 1)
            try:
                answer = self.all().filter(test_id=test_id)[random_index]
            except Exception as e:
                pass
        return answer


class RandomManager_expert_sciences(models.Manager):
    def random(self, sciences_id):
        answer = None
        while answer == None:
            count = self.aggregate(count=Count('id'))['count']
            random_index = randint(0, count - 1)
            try:
                answer = self.all().filter(type_sciences_id=sciences_id)[random_index]
            except Exception as e:
                pass
        return answer

class type_sciences(models.Model):
    sciences_name = models.CharField('Название науки', max_length=100, default=None)
    expert_count = models.PositiveSmallIntegerField('Число экспертов', default=0)

    class Meta:
        verbose_name = 'Вид науки'
        verbose_name_plural = 'Виды наук'
        db_table = 'type_sciences'

    def __str__(self):
        return self.sciences_name


class predmet(models.Model):
    predmet_name = models.CharField('Название предмета', max_length=256, default=None, unique=True)
    predmet_name_sokr = models.CharField('Название предмета сокращенно', max_length=20, default=None, unique=True)
    predmet_name_sokr_translite = models.CharField('Название предмета сокращенно англ', max_length=30, default=None,
                                                   blank=True, unique=True)
    type_sciences_id = models.ForeignKey(type_sciences, on_delete=models.CASCADE, verbose_name='Наука', default=None)

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
    status_test = models.CharField('Статус теста', choices=Test_Status_List.choices, default=Test_Status_List.Created,
                              max_length=3, blank=True)

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
    A_score = models.FloatField('Формализационная оценка', default=0)
    B_score = models.FloatField('Конструктивная оценка', default=0)
    C_score = models.FloatField('Исполнительская оценка', default=0)
    POL_score = models.FloatField('Исполнительская оценка', default=0)
    CHL_score = models.FloatField('Исполнительская оценка', default=0)

    objects = RandomManager_voprosi()

    def save(self, *args, **kwargs):
        self.otvet = self.otvet.lower()
        super(voprosi, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        db_table = 'voprosi'

    def __str__(self):
        return self.vopros + ' ' + self.otvet


class test_expert(models.Model):
    test_id = models.ForeignKey(test, on_delete=models.CASCADE, verbose_name='Тест')
    ocenka = models.PositiveSmallIntegerField('Средний балл', default=0, blank=True)
    check_status = models.BooleanField('Статус проверки', default=False, blank=True)
    override_status = models.BooleanField('Статус отправки на пересоставление теста', default=False, blank=True)

    class Meta:
        verbose_name = 'Экспертная проверка теста'
        verbose_name_plural = 'Экспертная проверка тестов'
        db_table = 'test_expert'

    def __str__(self):
        return f'{self.test_id}'

class test_expert_for_user(models.Model):
    test_expert_id = models.ForeignKey(test_expert, on_delete=models.CASCADE, verbose_name='Тест')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Эксперт')
    ocenka = models.PositiveSmallIntegerField('Оценка', default=0, blank=True)
    check_status = models.BooleanField('Статус проверки', default=False, blank=True)
    message = models.TextField('Рецензия', default='', blank=True, null=True)

    class Meta:
        verbose_name = 'Экспертная проверка теста ответ эксперта'
        verbose_name_plural = 'Экспертная проверка тестов ответы экспертов'
        db_table = 'test_expert_for_user'

    def __str__(self):
        return f'{self.test_expert_id}'


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


class expert_sciences(models.Model):
    type_sciences_id = models.ForeignKey(type_sciences, on_delete=models.CASCADE, verbose_name='Наука', default=None)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')

    objects = RandomManager_expert_sciences()

    class Meta:
        verbose_name = 'Наука эксперта'
        verbose_name_plural = 'Науки экспертов'
        db_table = 'expert_sciences'

    def __str__(self):
        return f'{self.user_id} {self.type_sciences_id}'

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
