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