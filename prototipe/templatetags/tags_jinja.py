from django import template
from django.contrib.auth.models import Group

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False

@register.filter(name='cheak_count_list')
def has_group(list):
    try:
        if len(list) > 0:
            return True
        else:
            return False
    except:
        return False

@register.filter(name='data_for_input')
def data_for_input(data):
    try:
        return data.strftime("%Y-%m-%d")
    except :
        return data

@register.filter(name='get_int')
def get_int(data):
    try:
        return int(data)
    except:
        return 0

@register.filter(name='to_js')
def to_js(data):
    local_data = []
    for i in data:
        local_data.append(i)
    return local_data

@register.filter(name='test_status')
def test_status(data):
    try:
        ocenka = int(data)
        if ocenka == 0:
            return 'Создание'
        elif ocenka == 1:
            return 'Отправлен на проверку'
        elif ocenka == 2:
            return 'Не прошел проверку, внесите правки'
        elif ocenka == 3:
            return 'Опубликован'
        elif ocenka == 4:
            return 'Удален'
        else:
            return 'Ошибка получения статуса'
    except:
        return 'Ошибка получения статуса'

@register.filter(name='access_edit')
def test_status(data):
    try:
        ocenka = int(data)
        if ocenka == 0:
            return True
        elif ocenka == 1:
            return False
        elif ocenka == 2:
            return True
        elif ocenka == 3:
            return False
        elif ocenka == 4:
            return False
        else:
            return False
    except:
        return False
