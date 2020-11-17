from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import type_sciences, test, predmet, voprosi, test_for_user, test_for_user_voprosi, test_expert, \
    test_expert_for_user, expert_sciences
from .forms import CreateTestForUserForm
from datetime import datetime, timedelta, time
from django.utils import timezone
from django.template.context_processors import csrf
from django.contrib.auth.models import User, Group


def get_marksCanvas(test_for_user_voprosi_object, ask_type):
    Sum = [0, 0, 0, 0, 0]
    Sum_all = [0, 0, 0, 0, 0]
    for i in test_for_user_voprosi_object:
        for index, item in enumerate(Sum):
            if i.otvet_status and index == 0:
                Sum[index] = Sum[index] + i.voprosi_id.A_score
            elif i.otvet_status and index == 1:
                Sum[index] = Sum[index] + i.voprosi_id.B_score
            elif i.otvet_status and index == 2:
                Sum[index] = Sum[index] + i.voprosi_id.C_score
            elif i.otvet_status and index == 3:
                Sum[index] = Sum[index] + i.voprosi_id.POL_score
            elif i.otvet_status and index == 4:
                Sum[index] = Sum[index] + i.voprosi_id.CHL_score

        for index, item in enumerate(Sum_all):
            if index == 0:
                Sum_all[index] = Sum_all[index] + i.voprosi_id.A_score
            elif index == 1:
                Sum_all[index] = Sum_all[index] + i.voprosi_id.B_score
            elif index == 2:
                Sum_all[index] = Sum_all[index] + i.voprosi_id.C_score
            elif index == 3:
                Sum_all[index] = Sum_all[index] + i.voprosi_id.POL_score
            elif index == 4:
                Sum_all[index] = Sum_all[index] + i.voprosi_id.CHL_score

    if ask_type == 0:
        return [round(Sum[0] / Sum_all[0] * 100, 1), round(Sum[1] / Sum_all[1] * 100, 1),
                round(Sum[2] / Sum_all[2] * 100, 1), round(Sum[3] / Sum_all[3] * 100, 1),
                round(Sum[4] / Sum_all[4] * 100, 1)]
    else:
        return [[Sum[0], Sum_all[0]], [Sum[1], Sum_all[1]], [Sum[2], Sum_all[2]], [Sum[3], Sum_all[3]],
                [Sum[4], Sum_all[4]]]


def get_user_all_stats(user_id):
    Sum = {}
    Sum_all = {}
    answer = []
    type_sciences_object = type_sciences.objects.all()
    for i in type_sciences_object:
        Sum[f'{i.sciences_name}'] = [0, 0, 0, 0, 0]
        Sum_all[f'{i.sciences_name}'] = [0, 0, 0, 0, 0]
        answer.append({"name": i.sciences_name, "result": [0, 0, 0, 0, 0]})
    try:
        test_for_user_object = test_for_user.objects.filter(user_id=user_id, end_status=True, override_status=False)
        for test in test_for_user_object:
            sciences_name = test.test_id.predmet_id.type_sciences_id.sciences_name
            test_for_user_voprosi_object = test_for_user_voprosi.objects.filter(test_for_user_id=test, user_id=user_id)
            local_stats = get_marksCanvas(test_for_user_voprosi_object, 1)

            Sum[f'{sciences_name}'] = [Sum[f'{sciences_name}'][0] + local_stats[0][0],
                                       Sum[f'{sciences_name}'][1] + local_stats[1][0],
                                       Sum[f'{sciences_name}'][2] + local_stats[2][0],
                                       Sum[f'{sciences_name}'][3] + local_stats[3][0],
                                       Sum[f'{sciences_name}'][4] + local_stats[4][0]]

            Sum_all[f'{sciences_name}'] = [Sum_all[f'{sciences_name}'][0] + local_stats[0][1],
                                           Sum_all[f'{sciences_name}'][1] + local_stats[1][1],
                                           Sum_all[f'{sciences_name}'][2] + local_stats[2][1],
                                           Sum_all[f'{sciences_name}'][3] + local_stats[3][1],
                                           Sum_all[f'{sciences_name}'][4] + local_stats[4][1]]

        for i, item in enumerate(answer):
            local_data = []
            for ind in range(5):
                if Sum_all[item["name"]][ind] == 0:
                    local_data.append(0)
                else:
                    local_data.append(round(Sum[item['name']][ind] / Sum_all[item['name']][ind] * 100, 1))
            answer[i]["result"] = local_data
    except:
        pass

    return answer


# def get_user_all_stats(user_id):
#     Sum = [0, 0, 0, 0, 0]
#     Sum_all = [0, 0, 0, 0, 0]
#     try:
#         test_for_user_object = test_for_user.objects.filter(user_id=user_id, end_status=True, override_status=False)
#         for test in test_for_user_object:
#             sciences_name = test.predmet_id.type_sciences_id.sciences_name
#             test_for_user_voprosi_object = test_for_user_voprosi.objects.filter(test_for_user_id=test, user_id=user_id)
#             local_stats = get_marksCanvas(test_for_user_voprosi_object, 1)
#
#             Sum = [Sum[0] + local_stats[0][0], Sum[1] + local_stats[1][0], Sum[2] + local_stats[2][0],
#                    Sum[3] + local_stats[3][0], Sum[4] + local_stats[4][0]]
#             Sum_all = [Sum_all[0] + local_stats[0][1], Sum_all[1] + local_stats[1][1], Sum_all[2] + local_stats[2][1],
#                    Sum_all[3] + local_stats[3][1], Sum_all[4] + local_stats[4][1]]
#         return [round(Sum[0] / Sum_all[0] * 100, 1), round(Sum[1] / Sum_all[1] * 100, 1),
#                 round(Sum[2] / Sum_all[2] * 100, 1), round(Sum[3] / Sum_all[3] * 100, 1),
#                 round(Sum[4] / Sum_all[4] * 100, 1)]
#     except:
#         return [0, 0, 0, 0, 0]

def get_ocenka_test(ocenka):
    if 0 < ocenka < 7:
        return False
    else:
        return True

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
                test_for_user_voprosi_object = test_for_user_voprosi.objects.filter(
                    test_for_user_id=test_for_user_object,
                    user_id=request.user)
                arguments.update(test_voprosi=test_for_user_voprosi_object)
                if test_for_user_object.end_status:
                    arguments.update(marksCanvas_data=get_marksCanvas(test_for_user_voprosi_object, 0))
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
            arguments.update(type_sciences=type_sciences.objects.all().order_by('sciences_name'))
            # return HttpResponse('админ', status=200)
            return render(request, 'prototipe/admin/predmets.html', {'arguments': arguments})
        elif request.method == 'POST':
            PredmetName = request.POST.get('PredmetName', False)
            SocrPredmetName = request.POST.get('SocrPredmetName', False)
            TypeSciences = request.POST.get('TypeSciences', False)
            if PredmetName and SocrPredmetName and TypeSciences:
                try:
                    type_sciences_object = type_sciences.objects.get(sciences_name=TypeSciences)
                    new_predmet = predmet(predmet_name=PredmetName, predmet_name_sokr=SocrPredmetName,
                                          type_sciences_id=type_sciences_object)
                    new_predmet.save()
                except:
                    arguments.update(error='Форма добавления заполнена не корректно!')
            else:
                arguments.update(error='Форма добавления заполнена не корректно!')
            arguments.update(predmets=predmet.objects.all().order_by('predmet_name'))
            arguments.update(type_sciences=type_sciences.objects.all().order_by('sciences_name'))
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
            TypeSciences = request.POST.get(f'TypeSciences_{predmet_id}', False)
            err = False
            if PredmetName and SocrPredmetName and TypeSciences:
                try:
                    type_sciences_object = type_sciences.objects.get(sciences_name=TypeSciences)
                except:
                    arguments.update(error='Данная наука не найдена в базе!')
                    err = True
                try:
                    if not err:
                        predmet_object = predmet.objects.get(id=predmet_id)
                        predmet_object.predmet_name = PredmetName
                        predmet_object.predmet_name_sokr = SocrPredmetName
                        predmet_object.type_sciences_id = type_sciences_object
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
                    test_object = test.objects.get(id=test_id)
                except:
                    arguments.update(error='Тест не найден!')
            elif has_group(request.user, 'Преподаватель'):
                try:
                    test_object = test.objects.get(id=test_id, create_user_id=request.user)
                except:
                    arguments.update(error='Тест не найден или его создали не вы!')
            else:
                arguments.update(error='Тест не найден!')
            try:
                arguments.update(test=test_object)
                arguments.update(voprosi=voprosi.objects.filter(test_id=test_object))
                test_expert_object = test_expert.objects.get(test_id=test_object)
                arguments.update(experts=test_expert_for_user.objects.filter(test_expert_id=test_expert_object))
            except:
                pass
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
            new_a = get_int(request.POST.get('new_a', ''))
            new_b = get_int(request.POST.get('new_b', ''))
            new_c = get_int(request.POST.get('new_c', ''))
            new_pol = get_int(request.POST.get('new_pol', ''))
            new_chl = get_int(request.POST.get('new_chl', ''))
            err = False
            test_search = False
            perem_status = False
            test_public_status = False
            if new_vopros and new_otvet and new_a > -1 and new_b > -1 and new_c > -1 and new_chl > -1 and new_pol > -1:
                if ((new_a + new_b + new_c) == 100) and (0 <= new_chl <= 100) and (0 <= new_pol <= 100):
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
                new_vopros = voprosi(test_id=test.objects.get(id=test_id), vopros=new_vopros, otvet=new_otvet,
                                     A_score=new_a, B_score=new_b, C_score=new_c, POL_score=new_pol, CHL_score=new_chl)
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
            perem_status = False
            for i, item in enumerate(request.POST):
                if 'vopros_' in item:
                    vopros_id = item.split('vopros_')[1]
                    break
            if vopros_id is not None:
                vopros = request.POST.get(f'vopros_{vopros_id}', False)
                otvet = request.POST.get(f'otvet_{vopros_id}', False)
                a = get_int(request.POST.get(f'a_{vopros_id}', False))
                b = get_int(request.POST.get(f'b_{vopros_id}', False))
                c = get_int(request.POST.get(f'c_{vopros_id}', False))
                pol = get_int(request.POST.get(f'pol_{vopros_id}', False))
                chl = get_int(request.POST.get(f'chl_{vopros_id}', False))
                if vopros and otvet and a > -1 and b > -1 and c > -1 and pol > -1 and chl > -1:
                    if ((a + b + c) == 100) and (0 <= chl <= 100) and (0 <= pol <= 100):
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
                else:
                    err = True
                    arguments.update(error='Форма заполнена не корректно!')
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
                vopros_object.A_score = a
                vopros_object.B_score = b
                vopros_object.C_score = c
                vopros_object.POL_score = pol
                vopros_object.CHL_score = chl
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
                # test_object.active_status = True
                try:
                    if int(test_object.status_test) == 0 or int(test_object.status_test) == 2:
                        test_expert_object = test_expert(test_id=test_object)
                        test_expert_object.save()
                        i = 0
                        count_expert = type_sciences.objects.get(
                            id=test_object.predmet_id.type_sciences_id.id).expert_count
                        while i < count_expert:
                            expert_object = expert_sciences.objects.random(test_object.predmet_id.type_sciences_id.id)
                            try:
                                test_expert_for_user.objects.get(test_expert_id=test_expert_object,
                                                                 user_id=expert_object.user_id)
                            except:
                                test_expert_for_user_object = test_expert_for_user(test_expert_id=test_expert_object,
                                                                                   user_id=expert_object.user_id)
                                test_expert_for_user_object.save()
                                i += 1

                        test_object.status_test = 1
                        test_object.save()
                except Exception as e:
                    print(e)

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
                    tests=test_for_user.objects.filter(test_id=test_id).order_by('-end_time'))
            return render(request, 'prototipe/admin/tests_for_archive.html', {'arguments': arguments})
        else:
            return HttpResponse('405 Method Not Allowed', status=405)
    else:
        return redirect('/')


def archive_user_answer_admin(request, test_id, user_answer_test_id):
    arguments = {}
    err = False
    if request.user.is_authenticated and (
            has_group(request.user, 'Администратор') or has_group(request.user, 'Преподаватель')):
        if request.method == 'GET':
            if has_group(request.user, 'Администратор'):
                try:
                    test_object = test.objects.get(id=test_id)
                except:
                    err = True
                    arguments.update(error='Тест не найден!')
            elif has_group(request.user, 'Преподаватель'):
                try:
                    test_object = test.objects.get(id=test_id, create_user_id=request.user)
                except:
                    err = True
                    arguments.update(error='Тест не найден или его создали не вы!')
            if not err:
                try:
                    test_for_user_object = test_for_user.objects.get(id=user_answer_test_id, test_id=test_object)
                    arguments.update(test=test_for_user_object)
                    test_for_user_voprosi_object = test_for_user_voprosi.objects.filter(
                        test_for_user_id=user_answer_test_id)
                    arguments.update(test_voprosi=test_for_user_voprosi_object)
                    if test_for_user_object.end_status:
                        arguments.update(marksCanvas_data=get_marksCanvas(test_for_user_voprosi_object, 0))
                except:
                    arguments.update(error='Тест не найден!')
            return render(request, 'prototipe/admin/test_for_archive.html', {'arguments': arguments})
        if request.method == 'POST':
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
    if request.user.is_authenticated and (
            has_group(request.user, 'Администратор') or has_group(request.user, 'Преподаватель')):
        if request.method == 'GET':
            arguments.update(users=User.objects.all().order_by('last_name').order_by('first_name').order_by(
                'userprofile__patronymic'))
            return render(request, 'prototipe/admin/users_list.html', {'arguments': arguments})
        else:
            return HttpResponse('405 Method Not Allowed', status=405)
    else:
        return redirect('/')


def user_look_admin(request, user_id):
    arguments = {}
    if request.user.is_authenticated and (
            has_group(request.user, 'Администратор') or has_group(request.user, 'Преподаватель')):
        if request.method == 'GET':
            try:
                arguments.update(user=User.objects.get(id=user_id))
                arguments.update(expert_data=expert_sciences.objects.filter(user_id=user_id))
                arguments.update(marksCanvas_data=get_user_all_stats(user_id))
                arguments.update(tests=test_for_user.objects.filter(user_id=user_id))
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
            if request.user.is_staff or request.user.is_superuser:
                is_staff = request.POST.get('is_staff', '')
                is_superuser = request.POST.get('is_superuser', '')

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


# TODO: EXPERT tests views
def expert_tests_list(request):
    arguments = {}
    if request.user.is_authenticated and has_group(request.user, 'Эксперт'):
        if request.method == 'GET':
            test_expert_for_user_object = test_expert_for_user.objects.filter(user_id=request.user, check_status=False)
            arguments.update(tests=test_expert_for_user_object)
            return render(request, 'prototipe/expert/tests_list.html', {'arguments': arguments})
        else:
            return HttpResponse('405 Method Not Allowed', status=405)
    else:
        return redirect('/')


def expert_test_look(request, test_id):
    arguments = {}
    err = False
    if request.user.is_authenticated and has_group(request.user, 'Эксперт'):
        if request.method == 'GET':
            try:
                test_expert_for_user_object = test_expert_for_user.objects.get(test_expert_id=test_id,
                                                                               user_id=request.user)
                arguments.update(test=test_expert_for_user_object)
                arguments.update(
                    voprosi=voprosi.objects.filter(test_id=test_expert_for_user_object.test_expert_id.test_id))
            except:
                arguments.update(error='Тест не найден!')
            return render(request, 'prototipe/expert/test.html', {'arguments': arguments})
        elif request.method == 'POST':
            review = request.POST.get('review', False)
            ocenka = request.POST.get('ocenka', False)

            try:
                test_expert_for_user_object = test_expert_for_user.objects.get(test_expert_id=test_id,
                                                                               user_id=request.user)
                arguments.update(test=test_expert_for_user_object)
                arguments.update(
                    voprosi=voprosi.objects.filter(test_id=test_expert_for_user_object.test_expert_id.test_id))
            except:
                err = True
                arguments.update(error='Тест не найден или уже оценен!')
            if review and get_int(ocenka) > 0:
                if not err:
                    test_expert_for_user_object.ocenka = get_int(ocenka)
                    test_expert_for_user_object.message = review
                    test_expert_for_user_object.check_status = True
                    test_expert_for_user_object.save()

                    test_expert_object = test_expert.objects.get(id=test_expert_for_user_object.test_expert_id.id)
                    test_expert_for_user_objects = test_expert_for_user.objects.filter(test_expert_id=test_expert_object)
                    validate_status = True
                    ocenka_sum = 0
                    expert_count = 0
                    for i, item in enumerate(test_expert_for_user_objects):
                        if not item.check_status:
                            validate_status = False
                        ocenka_sum += get_int(item.ocenka)
                        expert_count += 1

                    if validate_status:
                        new_ocenka_test = round(ocenka_sum / expert_count)
                        override_status = get_ocenka_test(new_ocenka_test)
                        test_expert_object.ocenka = new_ocenka_test
                        test_expert_object.check_status = True

                        test_object = test.objects.get(id=test_expert_object.test_id.id)
                        if override_status:
                            test_object.status_test = 3
                            test_object.active_status = True
                        else:
                            test_expert_object.override_status = True
                            test_object.status_test = 2
                        test_expert_object.save()
                        test_object.save()
            else:
                err = True
                arguments.update(error='Поле рецензии или оценки заполнены не корректно!')
            if err:
                return render(request, 'prototipe/expert/test.html', {'arguments': arguments})
            else:
                return redirect(f'/expert/tests/{test_id}')
        else:
            return HttpResponse('405 Method Not Allowed', status=405)
    else:
        return redirect('/')
