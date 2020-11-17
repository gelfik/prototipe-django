from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.template.context_processors import csrf

from prototipe.models import test_expert_for_user
from .forms import SignUpForm
from django.views.generic import View
from django.contrib.auth.models import Group
from userprofile.models import *


# Create your views here.
#
# class Register(View):
#     def get(self, request):
#         arguments = {}
#         arguments.update(csrf(request))
#         arguments.update(form=RegisterForm())
#         return render(request, 'myauth/register.html', {'arguments': arguments})
#
#     def post(self, request):
#         arguments = {}
#         arguments.update(csrf(request))
#         # arguments.update(form=RegisterForm())
#         bound_form = RegisterForm(request.POST)
#         if bound_form.is_valid():
#             new_user = bound_form.save()
#             new_user.refresh_from_db()
#             newuser = auth.authenticate(username=new_user.cleaned_data['username'], password=new_user.cleaned_data['password2'])
#             auth.login(request, newuser)
#             return redirect('/')
#         else:
#             arguments.update(form=bound_form)
#             return render(request, 'myauth/register.html', {'arguments': arguments})

def get_ocenka(all_count, valid_count):
    return round((valid_count / all_count) * 100)


def has_group(user, group_name):
    from django.contrib.auth.models import Group
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False


def get_int(value):
    try:
        return int(value)
    except:
        return -1

def login(request):
    arguments = {}
    arguments.update(csrf(request))
    if request.method == 'GET':
        return render(request, 'myauth/login.html')
    elif request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        userdata = auth.authenticate(username=username, password=password)
        try:
            usersearch = User.objects.get(username=username)
        except:
            usersearch = None
        if userdata is not None:
            auth.login(request, userdata)
            return redirect('/')
        elif usersearch is not None:
            arguments.update(login_error='Не верный пароль!')
            return render(request, 'myauth/login.html', {'arguments': arguments})
        else:
            arguments.update(login_error='Пользователь не найден!')
            return render(request, 'myauth/login.html', {'arguments': arguments})
    else:
        return HttpResponse('405 Method Not Allowed', status=405)


def logout(request):
    auth.logout(request)
    return redirect('/')


def register(request):
    arguments = {}
    arguments.update(csrf(request))
    arguments.update(form=SignUpForm)
    if request.user.is_anonymous:
        if request.method == 'GET':
            return render(request, 'myauth/register.html', {'arguments': arguments})
        elif request.method == 'POST':
            newuser_form = SignUpForm(request.POST)
            if newuser_form.is_valid():
                userform = newuser_form.save()
                userform.refresh_from_db()
                userform.userprofile.last_name = newuser_form.cleaned_data.get('last_name')
                userform.userprofile.first_name = newuser_form.cleaned_data.get('first_name')
                userform.userprofile.email = newuser_form.cleaned_data.get('email')
                userform.userprofile.patronymic = newuser_form.cleaned_data['patronymic']
                userform.userprofile.password = newuser_form.cleaned_data['password2']
                userform.set_password(newuser_form.cleaned_data['password2'])
                userform.save()
                userform.groups.add(Group.objects.get(name='Пользователь'))
                save_user_profile(sender=userform, instance=userform)
                newuser = auth.authenticate(username=newuser_form.cleaned_data['username'],
                                            password=newuser_form.cleaned_data['password2'])
                auth.login(request, newuser)
                return redirect('/')
            else:
                arguments.update(form=newuser_form)
                return render(request, 'myauth/register.html', {'arguments': arguments})
        else:
            return HttpResponse('405 Method Not Allowed', status=405)
    else:
        return redirect('/')

def user(request):
    arguments = {}
    if request.method == 'GET':
        if request.user.is_authenticated:
            count_expert_tests=test_expert_for_user.objects.filter(user_id=request.user, check_status=False).count()
            if has_group(request.user, 'Эксперт'):
                arguments.update(role='Эксперт')
                arguments.update(count_expert_tests=count_expert_tests)
            elif has_group(request.user, 'Преподаватель'):
                arguments.update(role='Преподаватель')
            elif has_group(request.user, 'Администратор'):
                arguments.update(role='Администратор')
            else:
                arguments.update(role='Пользователь')

            return JsonResponse(arguments, status=200)
        else:
            return HttpResponse('', status=401)
    else:
        return HttpResponse('405 Method Not Allowed', status=405)


# def register(request):
#     arguments = {}
#     arguments.update(csrf(request))
#     arguments.update(form=SignUpForm)
#     if request.user.is_anonymous:
#         if request.method == 'GET':
#             return render(request, 'myauth/register.html', {'arguments': arguments})
#         elif request.method == 'POST':
#             newuser_form = SignUpForm(request.POST)
#             if newuser_form.is_valid():
#                 userform = newuser_form.save()
#                 userform.refresh_from_db()
#                 userform.userprofile.last_name = newuser_form.cleaned_data.get('last_name')
#                 userform.userprofile.first_name = newuser_form.cleaned_data.get('first_name')
#                 userform.userprofile.email = newuser_form.cleaned_data.get('email')
#                 userform.save()
#                 newuser = auth.authenticate(username=newuser_form.cleaned_data['username'], password=newuser_form.cleaned_data['password2'])
#                 auth.login(request, newuser)
#                 return redirect('/')
#             else:
#                 arguments.update(form=newuser_form)
#                 return render(request, 'myauth/register.html', {'arguments': arguments})
#         else:
#             return HttpResponse('405 Method Not Allowed', status=405)
#     else:
#         return redirect('/')
