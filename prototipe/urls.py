"""MIPS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, re_path, include
from . import views

urlpatterns = [
    path('', views.index),

    re_path(r'^adm/predmets/([0-9]+)', views.predmets_admin_edit_del),
    path('adm/predmets', views.predmets_admin),

    re_path(r'^adm/tests/([0-9]+)/(addVopros|editTest|editVopros|publicTest|delTest)', views.tests_admin_edit_test),
    re_path(r'^adm/tests/([0-9]+)', views.tests_admin_look),
    path('adm/tests', views.tests_admin),

    re_path(r'^adm/archive/([0-9]+)/([0-9]+)', views.archive_user_answer_admin),
    re_path(r'^adm/archive/([0-9]+)', views.archive_users_list_admin),
    path('adm/archive', views.archive_admin),

    re_path(r'^adm/users/([0-9]+)/(editUser|delUser|setExpert)', views.user_manage_admin),
    re_path(r'^adm/users/([0-9]+)', views.user_look_admin),
    path('adm/users', views.users_list_admin),

    re_path(r'^expert/tests/([0-9]+)/(answer)', views.user_manage_admin),
    re_path(r'^expert/tests/([0-9]+)', views.expert_test_look),
    path('expert/tests', views.expert_tests_list),

    path('tests', views.predmets_list),
    re_path(r'^tests/([A-z0-9]+)/([A-z0-9]+)/([A-z0-9]+)', views.test_for_test),
    re_path(r'^tests/([A-z0-9]+)/([A-z0-9]+)', views.test_for_test_generate),
    re_path(r'^tests/([A-z0-9]+)', views.test_for_predmet),

    # re_path(r'^predmets/([0-9]+)', views.tests_query),
    # path('tests', views.tests),
    # re_path(r'^tests/([0-9]+)', views.tests_query),
]
