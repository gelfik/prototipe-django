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