from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import test, predmet, voprosi, test_for_user, test_for_user_voprosi
from .forms import CreateTestForUserForm
from datetime import datetime, timedelta, time
from django.utils import timezone
from django.template.context_processors import csrf
from django.contrib.auth.models import User, Group


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
        return False


# Create your views here.

def index(request):
    if request.method == "GET":
        arguments = {}
        arguments.update(role='student')
        if not request.COOKIES.get('role'):
            response = render(request, 'prototipe/index.html', {'arguments': arguments})
            response.set_cookie(key='role', value='student')
        else:
            if request.COOKIES.get('role') == 'student':
                response = render(request, 'prototipe/index.html', {'arguments': arguments})
            else:
                arguments.update(role='teacher')
                response = render(request, 'prototipe/index.html', {'arguments': arguments})
        return response
    else:
        return HttpResponse('405 Method Not Allowed', status=405)


def predmets_list(request):
    arguments = {}
    for i, j in enumerate(request.user.groups.all()):
        if 'Преподаватель' in str(j):
            print('')
    if request.user.is_authenticated:
        if request.method == 'GET':
            arguments.update(predmets=predmet.objects.all())
            return render(request, 'prototipe/predmetlist.html', {'arguments': arguments})
        else:
            return HttpResponse('405 Method Not Allowed', status=405)
    else:
        return redirect('/')


def test_for_predmet(request, predmet_name):
    arguments = {}
    if request.user.is_authenticated:
        if request.method == 'GET':
            try:
                predmet_object = predmet.objects.get(predmet_name_sokr_translite=predmet_name)
                arguments.update(predmet=predmet_object)
                arguments.update(tests=test.objects.all().filter(predmet_id=predmet_object, active_status=True,
                                                                 valid_date__gte=datetime.now(tz=timezone.utc)))
            except:
                pass
            return render(request, 'prototipe/testlist.html', {'arguments': arguments})
        else:
            return HttpResponse('405 Method Not Allowed', status=405)
    else:
        return redirect('/')


def test_for_test(request, predmet_name, test_id, test_id_for_user):
    arguments = {}
    arguments.update(csrf(request))
    if request.user.is_authenticated:
        if request.method == 'GET':
            try:
                predmet_object = predmet.objects.get(predmet_name_sokr_translite=predmet_name)
                arguments.update(predmet=predmet_object)
                test_object = test.objects.all().get(predmet_id=predmet_object, id=test_id, active_status=True,
                                                     valid_date__gte=datetime.now(tz=timezone.utc))
                arguments.update(test=test_object)
                test_for_user_object = test_for_user.objects.get(test_id=test_object, user_id=request.user,
                                                                 id=test_id_for_user)
                arguments.update(test_for_user=test_for_user_object)
                test_for_user_voprosi_object = test_for_user_voprosi.objects.filter(test_for_user_id=test_for_user_object,
                                                                            user_id=request.user)
                print(test_for_user_voprosi_object.count())
                arguments.update(test_voprosi=test_for_user_voprosi_object)
            except:
                pass
                # return HttpResponse(e, status=405)
            return render(request, 'prototipe/test.html', {'arguments': arguments})
        elif request.method == 'POST':
            count_ask = 0
            answer_dict = {}
            for i, item in enumerate(request.POST):
                if 'ask_' in item:
                    count_ask += 1
                    answer_dict[item.split('ask_')[1]] = request.POST[item].lower()
            error_message = ''
            try:
                error_message = 'Предмет не найден!'
                predmet_object = predmet.objects.get(predmet_name_sokr_translite=predmet_name)
                arguments.update(predmet=predmet_object)
                error_message = 'Тест не найден!'
                test_object = test.objects.all().get(predmet_id=predmet_object, id=test_id, active_status=True)
                arguments.update(test=test_object)
                error_message = 'Для вас тесты не найдены!'
                test_for_user_object = test_for_user.objects.get(test_id=test_object, user_id=request.user,
                                                                 end_status=False)
                test_voprosi = test_for_user_voprosi.objects.all().filter(test_for_user_id=test_for_user_object,
                                                                          user_id=request.user)
                if len(test_voprosi) == count_ask:
                    for i, item in enumerate(answer_dict):
                        try:
                            update_test = test_for_user_voprosi.objects.get(test_for_user_id=test_for_user_object,
                                                                            user_id=request.user,
                                                                            voprose_num=item)
                            update_test.otvet_user = answer_dict[item]
                            vopros_object = voprosi.objects.get(id=update_test.voprosi_id.id)
                            if vopros_object.otvet == answer_dict[item]:
                                update_test.otvet_status = True
                            else:
                                update_test.otvet_status = False
                            update_test.save()
                        except:
                            error_message = 'Ответы на вопросы отправлены не корректно!'
                    user_voprosi_valid_count = test_for_user_voprosi.objects.all().filter(
                        test_for_user_id=test_for_user_object, user_id=request.user, otvet_status=True).count()
                    test_for_user_object.ocenka = get_ocenka(test_object.voprosi_count, user_voprosi_valid_count)
                    test_for_user_object.end_time = datetime.now(tz=timezone.utc)
                    test_for_user_object.end_status = True
                    test_for_user_object.save()
                else:
                    error_message = 'Ответы на вопросы отправлены не корректно!'
                arguments.update(test_for_user=test_for_user_object)
            except Exception as e:
                arguments.update(error_message=error_message)
                return render(request, 'prototipe/test.html', {'arguments': arguments})
            return redirect(f'/tests/{predmet_name}/{test_id}/{test_id_for_user}')
        else:
            return HttpResponse('405 Method Not Allowed', status=405)
    else:
        return redirect('/')


def test_for_test_generate(request, predmet_name, test_id):
    arguments = {}
    arguments.update(csrf(request))
    if request.user.is_authenticated:
        if request.method == 'GET':
            try:
                predmet_object = predmet.objects.get(predmet_name_sokr_translite=predmet_name)
                arguments.update(predmet=predmet_object)
                test_object = test.objects.get(predmet_id=predmet_object, id=test_id, active_status=True,
                                               valid_date__gte=datetime.now(tz=timezone.utc))
                try:
                    try:
                        test_for_user_object = test_for_user.objects.get(test_id=test_object, user_id=request.user,
                                                                         end_status=False)
                    except:
                        test_for_user_object = test_for_user.objects.get(test_id=test_object, user_id=request.user,
                                                                         end_status=True, override_status=False)
                except:
                    test_for_user_object = test_for_user(test_id=test_object, user_id=request.user,
                                                         start_time=datetime.now(tz=timezone.utc))
                    test_for_user_object.save()
                    i = 0
                    while i < test_object.voprosi_count:
                        voprosi_object = voprosi.objects.random(test_object.id)
                        try:
                            test_for_user_voprosi.objects.get(test_for_user_id=test_for_user_object,
                                                              user_id=request.user,
                                                              voprosi_id=voprosi_object)
                        except:
                            test_for_user_voprosi_object = test_for_user_voprosi(test_for_user_id=test_for_user_object,
                                                                                 user_id=request.user,
                                                                                 voprosi_id=voprosi_object,
                                                                                 voprose_num=i + 1)
                            test_for_user_voprosi_object.save()
                            i += 1
                    # for i in range(test_object.voprosi_count):
                    #     test_for_user_voprosi_object = test_for_user_voprosi(test_for_user_id=test_for_user_object,
                    #                                                          user_id=request.user,
                    #                                                          voprosi_id=voprosi.objects.random(
                    #                                                              test_object.id), voprose_num=i + 1)
                    #     test_for_user_voprosi_object.save()
                return redirect(f'/tests/{predmet_name}/{test_id}/{test_for_user_object.id}')
            except:
                return render(request, 'prototipe/test.html', {'arguments': arguments})
        else:
            return HttpResponse('405 Method Not Allowed', status=405)
    else:
        return redirect('/')


# TODO: ADMIN PREDMETS views
def predmets_admin(request):
    arguments = {}
    if request.user.is_authenticated and has_group(request.user, 'Администратор'):
        if request.method == 'GET':
            arguments.update(predmets=predmet.objects.all().order_by('predmet_name'))
            # return HttpResponse('админ', status=200)
            return render(request, 'prototipe/admin/predmets.html', {'arguments': arguments})
        elif request.method == 'POST':
            PredmetName = request.POST.get('PredmetName', False)
            SocrPredmetName = request.POST.get('SocrPredmetName', False)
            if PredmetName and SocrPredmetName:
                new_predmet = predmet(predmet_name=PredmetName, predmet_name_sokr=SocrPredmetName)
                new_predmet.save()
            else:
                arguments.update(error='Форма добавления заполнена не корректно!')
            arguments.update(predmets=predmet.objects.all().order_by('predmet_name'))
            return render(request, 'prototipe/admin/predmets.html', {'arguments': arguments})
        else:
            return HttpResponse('405 Method Not Allowed', status=405)
    else:
        return redirect('/')


def predmets_admin_edit_del(request, predmet_id):
    arguments = {}
    if request.user.is_authenticated and has_group(request.user, 'Администратор'):
        if request.method == 'GET':
            err = False
            try:
                predmet_object = predmet.objects.get(id=predmet_id)
                predmet_object.delete()
            except:
                arguments.update(error='Предмет не найден в базе!')
                err = True
            if err:
                arguments.update(predmets=predmet.objects.all().order_by('predmet_name'))
                return render(request, 'prototipe/admin/predmets.html', {'arguments': arguments})
            else:
                return redirect('/adm/predmets')
        elif request.method == 'POST':
            PredmetName = request.POST.get(f'PredmetName_{predmet_id}', False)
            SocrPredmetName = request.POST.get(f'SocrPredmetName_{predmet_id}', False)
            err = False
            if PredmetName and SocrPredmetName:
                try:
                    predmet_object = predmet.objects.get(id=predmet_id)
                    predmet_object.predmet_name = PredmetName
                    predmet_object.predmet_name_sokr = SocrPredmetName
                    predmet_object.save()
                except:
                    arguments.update(error='Предмет не найден в базе!')
                    err = True
            else:
                arguments.update(error='Форма редактирования заполнена не корректно!')
                err = True
            if err:
                arguments.update(predmets=predmet.objects.all().order_by('predmet_name'))
                return render(request, 'prototipe/admin/predmets.html', {'arguments': arguments})
            else:
                return redirect('/adm/predmets')
        else:
            return HttpResponse('405 Method Not Allowed', status=405)
    else:
        return redirect('/')


# TODO: ADMIN TESTS views
def tests_admin(request):
    arguments = {}
    if request.user.is_authenticated and (
            has_group(request.user, 'Администратор') or has_group(request.user, 'Преподаватель')):
        if request.method == 'GET':
            arguments.update(predmets=predmet.objects.all())
            if has_group(request.user, 'Администратор'):
                arguments.update(tests=test.objects.all())
            elif has_group(request.user, 'Преподаватель'):
                arguments.update(tests=test.objects.filter(create_user_id=request.user))
            return render(request, 'prototipe/admin/predmets_for_tests.html', {'arguments': arguments})
        elif request.method == 'POST':
            test_name = request.POST.get('test_name', False)
            valid_date = request.POST.get('valid_date', False)
            predmet_id = request.POST.get('predmet_id', False)
            err = False
            if test_name and valid_date and predmet_id:
                try:
                    predmet_object = predmet.objects.get(id=predmet_id)
                    new_test = test(test_name=test_name, valid_date=valid_date, predmet_id=predmet_object,
                                    create_user_id=request.user)
                    new_test.save()
                except Exception as e:
                    err = True
                    arguments.update(error='Предмет не найден в базе!')
            else:
                err = True
                arguments.update(error='Форма добавления теста заполнена не корректно!')
            if err:
                if has_group(request.user, 'Администратор'):
                    arguments.update(tests=test.objects.all())
                elif has_group(request.user, 'Преподаватель'):
                    arguments.update(tests=test.objects.filter(create_user_id=request.user))
                return render(request, 'prototipe/admin/predmets_for_tests.html', {'arguments': arguments})
            else:
                return redirect(f'/adm/tests/{new_test.id}')
        else:
            return HttpResponse('405 Method Not Allowed', status=405)
    else:
        return redirect('/')


def tests_admin_look(request, test_id):
    arguments = {}
    if request.user.is_authenticated and (
            has_group(request.user, 'Администратор') or has_group(request.user, 'Преподаватель')):
        if request.method == 'GET':
            if has_group(request.user, 'Администратор'):
                try:
                    arguments.update(test=test.objects.get(id=test_id))
                    arguments.update(voprosi=voprosi.objects.filter(test_id=test_id))
                except:
                    arguments.update(error='Тест не найден!')
            elif has_group(request.user, 'Преподаватель'):
                try:
                    arguments.update(test=test.objects.get(id=test_id, create_user_id=request.user))
                    arguments.update(voprosi=voprosi.objects.filter(test_id=test_id))
                except:
                    arguments.update(error='Тест не найден или его создали не вы!')
            else:
                arguments.update(error='Тест не найден!')
            return render(request, 'prototipe/admin/test.html', {'arguments': arguments})
        else:
            return HttpResponse('405 Method Not Allowed', status=405)
    else:
        return redirect('/')


def tests_admin_edit_test(request, test_id, query_type):
    arguments = {}
    if request.user.is_authenticated and (
            has_group(request.user, 'Администратор') or has_group(request.user, 'Преподаватель')):
        if request.method == 'POST' and query_type == 'addVopros':
            new_vopros = request.POST.get('new_vopros', '')
            new_otvet = request.POST.get('new_otvet', '')
            err = False
            test_search = False
            perem_status = False
            test_public_status = False
            if new_vopros and new_otvet:
                perem_status = True
            if has_group(request.user, 'Администратор'):
                try:
                    arguments.update(test=test.objects.get(id=test_id))
                    test_search = True
                except:
                    arguments.update(error='Тест не найден!')
                    err = True
            elif has_group(request.user, 'Преподаватель'):
                try:
                    arguments.update(test=test.objects.get(id=test_id, create_user_id=request.user))
                    test_search = True
                except:
                    arguments.update(error='Тест не найден или его создали не вы!')
                    err = True
            else:
                arguments.update(error='Тест не найден!')
                err = True
            try:
                test.objects.get(id=test_id, active_status=False)
            except:
                arguments.update(error='Тест опубликован, в него нельзя добавлять вопросы!')
                test_public_status = True
            if not perem_status:
                arguments.update(error='Форма добавления вопроса заполнена не корректно!')
            if err or not perem_status or test_public_status:
                if test_search:
                    arguments.update(voprosi=voprosi.objects.filter(test_id=test_id))
                return render(request, 'prototipe/admin/test.html', {'arguments': arguments})
            else:
                new_vopros = voprosi(test_id=test.objects.get(id=test_id), vopros=new_vopros, otvet=new_otvet)
                new_vopros.save()
                return redirect(f'/adm/tests/{test_id}')
        if request.method == 'POST' and query_type == 'editTest':
            vopros_count = request.POST.get('vopros_count', False)
            test_name = request.POST.get('test_name', False)
            valid_date = request.POST.get('valid_date', False)
            err = False
            perem_status = False
            test_search = False
            test_public_status = False
            if vopros_count and test_name and valid_date:
                perem_status = True
            if has_group(request.user, 'Администратор'):
                try:
                    arguments.update(test=test.objects.get(id=test_id))
                    test_search = True
                except:
                    arguments.update(error='Тест не найден!')
                    err = True
            elif has_group(request.user, 'Преподаватель'):
                try:
                    arguments.update(test=test.objects.get(id=test_id, create_user_id=request.user))
                    test_search = True
                except:
                    arguments.update(error='Тест не найден или его создали не вы!')
                    err = True
            else:
                arguments.update(error='Тест не найден!')
                err = True
            try:
                test.objects.get(id=test_id, active_status=False)
            except:
                arguments.update(error='Тест опубликован, в него нельзя вносить изменения!')
                test_public_status = True
            if not perem_status:
                arguments.update(error='Форма заполнена не корректно!')
            if err or not perem_status or test_public_status:
                if test_search:
                    arguments.update(voprosi=voprosi.objects.filter(test_id=test_id))
                return render(request, 'prototipe/admin/test.html', {'arguments': arguments})
            else:
                new_vopros = test.objects.get(id=test_id)
                new_vopros.voprosi_count = vopros_count
                new_vopros.test_name = test_name
                new_vopros.valid_date = valid_date
                new_vopros.save()
                return redirect(f'/adm/tests/{test_id}')

        if request.method == 'POST' and query_type == 'editVopros':
            vopros_id = None
            err = False
            test_search = False
            test_public_status = False
            for i, item in enumerate(request.POST):
                if 'vopros_' in item:
                    vopros_id = item.split('vopros_')[1]
                    break
            if vopros_id is not None:
                vopros = request.POST.get(f'vopros_{vopros_id}', False)
                otvet = request.POST.get(f'otvet_{vopros_id}', False)
                if has_group(request.user, 'Администратор'):
                    try:
                        arguments.update(test=test.objects.get(id=test_id))
                        test_search = True
                    except:
                        arguments.update(error='Тест не найден!')
                        err = True
                elif has_group(request.user, 'Преподаватель'):
                    try:
                        arguments.update(test=test.objects.get(id=test_id, create_user_id=request.user))
                        test_search = True
                    except:
                        arguments.update(error='Тест не найден или его создали не вы!')
                        err = True
                else:
                    arguments.update(error='Тест не найден!')
                    err = True
                try:
                    test.objects.get(id=test_id, active_status=False)
                except:
                    arguments.update(error='Тест опубликован, в него нельзя вносить изменения!')
                    test_public_status = True
            else:
                err = True
                arguments.update(error='Форма заполнена не корректно!')
            try:
                vopros_object = voprosi.objects.get(id=vopros_id)
            except:
                err = True
                arguments.update(error='Вопрос не найден в базе!')
            if err or test_public_status:
                if test_search:
                    arguments.update(voprosi=voprosi.objects.filter(test_id=test_id))
                return render(request, 'prototipe/admin/test.html', {'arguments': arguments})
            else:
                vopros_object.vopros = vopros
                vopros_object.otvet = otvet
                vopros_object.save()
                return redirect(f'/adm/tests/{test_id}')

        if request.method == 'GET' and query_type == 'editVopros':
            vopros_id = None
            err = False
            test_search = False
            test_public_status = False
            for i, item in enumerate(request.GET):
                if 'vopros_' in item:
                    vopros_id = item.split('vopros_')[1]
                    break
            if vopros_id is not None:
                if has_group(request.user, 'Администратор'):
                    try:
                        arguments.update(test=test.objects.get(id=test_id))
                        test_search = True
                    except:
                        arguments.update(error='Тест не найден!')
                        err = True
                elif has_group(request.user, 'Преподаватель'):
                    try:
                        arguments.update(test=test.objects.get(id=test_id, create_user_id=request.user))
                        test_search = True
                    except:
                        arguments.update(error='Тест не найден или его создали не вы!')
                        err = True
                else:
                    arguments.update(error='Тест не найден!')
                    err = True
                try:
                    test.objects.get(id=test_id, active_status=False)
                except:
                    arguments.update(error='Тест опубликован, в него нельзя вносить изменения!')
                    test_public_status = True
                try:
                    voprosi.objects.get(id=vopros_id).delete()
                except:
                    err = True
                    arguments.update(error='Вопрос не найден в базе!')
            else:
                err = True
                arguments.update(error='Форма заполнена не корректно!')
            if err or test_public_status:
                if test_search:
                    arguments.update(voprosi=voprosi.objects.filter(test_id=test_id))
                return render(request, 'prototipe/admin/test.html', {'arguments': arguments})
            else:
                return redirect(f'/adm/tests/{test_id}')

        if request.method == 'POST' and query_type == 'publicTest':
            err = False
            test_search = False
            test_public_status = False
            if has_group(request.user, 'Администратор'):
                try:
                    arguments.update(test=test.objects.get(id=test_id))
                    test_search = True
                except:
                    arguments.update(error='Тест не найден!')
                    err = True
            elif has_group(request.user, 'Преподаватель'):
                try:
                    arguments.update(test=test.objects.get(id=test_id, create_user_id=request.user))
                    test_search = True
                except:
                    arguments.update(error='Тест не найден или его создали не вы!')
                    err = True
            else:
                arguments.update(error='Тест не найден!')
                err = True
            try:
                test.objects.get(id=test_id, active_status=False)
            except:
                arguments.update(error='Тест опубликован, в него нельзя вносить изменения!')
                test_public_status = True

            if test_search and not test_public_status:
                voprosi_object = voprosi.objects.filter(test_id=test_id).count()
                test_object = test.objects.get(id=test_id)
                if voprosi_object < test_object.voprosi_count:
                    arguments.update(error='Выборка из вопросов, больше чем число вопросов!')
                    err = True

            if err or test_public_status:
                if test_search:
                    arguments.update(voprosi=voprosi.objects.filter(test_id=test_id))
                return render(request, 'prototipe/admin/test.html', {'arguments': arguments})
            else:
                test_object = test.objects.get(id=test_id)
                test_object.active_status = True
                test_object.save()
                return redirect(f'/adm/tests/{test_id}')

        if request.method == 'POST' and query_type == 'delTest':
            err = False
            test_search = False
            if has_group(request.user, 'Администратор'):
                try:
                    arguments.update(test=test.objects.get(id=test_id))
                    test_search = True
                except:
                    arguments.update(error='Тест не найден!')
                    err = True
            elif has_group(request.user, 'Преподаватель'):
                try:
                    arguments.update(test=test.objects.get(id=test_id, create_user_id=request.user))
                    test_search = True
                except:
                    arguments.update(error='Тест не найден или его создали не вы!')
                    err = True
            else:
                arguments.update(error='Тест не найден!')
                err = True

            if err:
                if test_search:
                    arguments.update(voprosi=voprosi.objects.filter(test_id=test_id))
                return render(request, 'prototipe/admin/test.html', {'arguments': arguments})
            else:
                test_object = test.objects.get(id=test_id)
                test_object.delete()
                return redirect(f'/adm/tests/{test_id}')

        else:
            return HttpResponse('405 Method Not Allowed', status=405)
    else:
        return redirect('/')


# TODO: ADMIN archive views
def archive_admin(request):
    arguments = {}
    if request.user.is_authenticated and (
            has_group(request.user, 'Администратор') or has_group(request.user, 'Преподаватель')):
        if request.method == 'GET':
            if has_group(request.user, 'Администратор'):
                arguments.update(tests=test.objects.all().order_by('valid_date'))
            elif has_group(request.user, 'Преподаватель'):
                arguments.update(tests=test.objects.filter(create_user_id=request.user).order_by('valid_date'))
            return render(request, 'prototipe/admin/predmets_for_archive.html', {'arguments': arguments})
        else:
            return HttpResponse('405 Method Not Allowed', status=405)
    else:
        return redirect('/')


def archive_users_list_admin(request, test_id):
    arguments = {}
    if request.user.is_authenticated and (
            has_group(request.user, 'Администратор') or has_group(request.user, 'Преподаватель')):
        if request.method == 'GET':
            if has_group(request.user, 'Администратор'):
                arguments.update(test=test.objects.get(id=test_id))
                arguments.update(
                    tests=test_for_user.objects.filter(test_id=test_id).order_by('-end_time'))
            elif has_group(request.user, 'Преподаватель'):
                arguments.update(test=test.objects.get(id=test_id, create_user_id=request.user))
                arguments.update(
                    tests=test_for_user.objects.filter(create_user_id=request.user, test_id=test_id).order_by('-end_time'))
            return render(request, 'prototipe/admin/tests_for_archive.html', {'arguments': arguments})
        else:
            return HttpResponse('405 Method Not Allowed', status=405)
    else:
        return redirect('/')

def archive_user_answer_admin(request, test_id, user_answer_test_id):
    arguments = {}
    if request.user.is_authenticated and (
            has_group(request.user, 'Администратор') or has_group(request.user, 'Преподаватель')):
        if request.method == 'GET':
            if has_group(request.user, 'Администратор'):
                try:
                    test_object = test.objects.get(id=test_id)
                    arguments.update(test=test_for_user.objects.get(id=user_answer_test_id, test_id=test_object))
                    arguments.update(test_voprosi=test_for_user_voprosi.objects.filter(test_for_user_id=user_answer_test_id))
                except:
                    arguments.update(error='Тест не найден!')
            elif has_group(request.user, 'Преподаватель'):
                try:
                    test_object = test.objects.get(id=test_id, create_user_id=request.user)
                    arguments.update(test=test_for_user.objects.get(id=user_answer_test_id, test_id=test_object))
                    arguments.update(test_voprosi=test_for_user_voprosi.objects.filter(test_for_user_id=user_answer_test_id))
                except:
                    arguments.update(error='Тест не найден или его создали не вы!')
            return render(request, 'prototipe/admin/test_for_archive.html', {'arguments': arguments})
        if request.method == 'POST':
            err = False
            if has_group(request.user, 'Администратор'):
                try:
                    test_object = test.objects.get(id=test_id)
                    test_for_user_object = test_for_user.objects.get(id=user_answer_test_id, test_id=test_object)
                except:
                    err = True
                    arguments.update(error='Тест не найден!')
            elif has_group(request.user, 'Преподаватель'):
                try:
                    test_object = test.objects.get(id=test_id, create_user_id=request.user)
                    test_for_user_object = test_for_user.objects.get(id=user_answer_test_id, test_id=test_object)
                except:
                    err = True
                    arguments.update(error='Тест не найден или его создали не вы!')
            if err:
                return render(request, 'prototipe/admin/test_for_archive.html', {'arguments': arguments})
            else:
                test_for_user_object.override_status = True
                test_for_user_object.save()
                return redirect(f'/adm/archive/{test_id}/{user_answer_test_id}')
        else:
            return HttpResponse('405 Method Not Allowed', status=405)
    else:
        return redirect('/')

def users_list_admin(request):
    arguments = {}
    if request.user.is_authenticated and has_group(request.user, 'Администратор'):
        if request.method == 'GET':
            arguments.update(users=User.objects.all().order_by('last_name').order_by('first_name').order_by('userprofile__patronymic'))
            return render(request, 'prototipe/admin/users_list.html', {'arguments': arguments})
        else:
            return HttpResponse('405 Method Not Allowed', status=405)
    else:
        return redirect('/')

def user_look_admin(request, user_id):
    arguments = {}
    if request.user.is_authenticated and has_group(request.user, 'Администратор'):
        if request.method == 'GET':
            try:
                arguments.update(user=User.objects.get(id=user_id))
            except:
                arguments.update(error='Пользователь не найден!')
            return render(request, 'prototipe/admin/user_look.html', {'arguments': arguments})
        else:
            return HttpResponse('405 Method Not Allowed', status=405)
    else:
        return redirect('/')


def user_manage_admin(request, user_id, query_type):
    arguments = {}
    if request.user.is_authenticated and has_group(request.user, 'Администратор'):
        if request.method == 'POST' and query_type == 'editUser':
            err = False
            user_search = False
            args_status = False
            last_name = request.POST.get('last_name', False)
            first_name = request.POST.get('first_name', False)
            patronymic = request.POST.get('patronymic', False)
            username = request.POST.get('username', False)
            email = request.POST.get('email', False)
            user_group = request.POST.get('user_group', False)
            print(f'{user_group}')
            if request.user.is_staff or request.user.is_superuser:
                is_staff = request.POST.get('is_staff', '')
                is_superuser = request.POST.get('is_superuser', '')
                print(f'111 {is_staff} {is_superuser}')

            if last_name and first_name and patronymic and username and email and user_group:
                args_status = True
                if request.user.is_staff or request.user.is_superuser:
                    if is_staff != '' and is_superuser != '':
                        args_status = True
                    else:
                        args_status = False
            else:
                arguments.update(error='Форма заполнена не корректно!')
            try:
                user_object = User.objects.get(id=user_id)
                user_search = True
            except:
                arguments.update(error='Пользователь не найден!')
                err = True
            if err or not args_status:
                if user_search:
                    arguments.update(user=user_object)
                return render(request, 'prototipe/admin/user_look.html', {'arguments': arguments})
            else:
                user_object = User.objects.get(id=user_id)
                user_object.last_name = last_name
                user_object.first_name = first_name
                user_object.userprofile.patronymic = patronymic
                user_object.username = username
                user_object.email = email
                user_object.groups.clear()
                user_object.groups.add(Group.objects.get(name=user_group))
                if request.user.is_staff or request.user.is_superuser:
                    user_object.is_staff = is_staff
                    user_object.is_superuser = is_superuser
                user_object.save()
                return redirect(f'/adm/users/{user_id}')
        if request.method == 'POST' and query_type == 'delUser':
            err = False
            user_search = False
            try:
                user_object = User.objects.get(id=user_id)
                user_search = True
            except:
                arguments.update(error='Пользователь не найден!')
                err = True
            if err:
                if user_search:
                    arguments.update(user=user_object)
                return render(request, 'prototipe/admin/user_look.html', {'arguments': arguments})
            else:
                if user_search:
                    user_object.delete()
                return redirect(f'/adm/users')
        else:
            return HttpResponse('405 Method Not Allowed', status=405)
    else:
        return redirect('/')