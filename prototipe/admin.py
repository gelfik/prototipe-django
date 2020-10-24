from django.contrib import admin
from django.contrib.auth.models import User
from .models import type_sciences, predmet, test, voprosi, test_for_user, test_for_user_voprosi
# from .models import user_data, users_lvl, auth_token
# Register your models here.

@admin.register(type_sciences)
class type_sciences_list(admin.ModelAdmin):
    list_display = ['sciences_name']

@admin.register(predmet)
class predmet_list(admin.ModelAdmin):
    list_display = ('predmet_name_sokr', 'predmet_name', 'type_sciences_id', 'predmet_name_sokr_translite')

@admin.register(test)
class test_list(admin.ModelAdmin):
    list_display = ('test_name', 'valid_date', 'predmet_id', 'voprosi_count', 'create_user_id')

@admin.register(voprosi)
class voprosi_list(admin.ModelAdmin):
    list_display = ('vopros', 'otvet', 'test_id', 'A_score' , 'B_score' , 'C_score' , 'POL_score' , 'CHL_score')

@admin.register(test_for_user)
class test_for_user(admin.ModelAdmin):
    list_display = ('test_id', 'user_id', 'start_time', 'end_time', 'ocenka', 'end_status', 'override_status')

@admin.register(test_for_user_voprosi)
class test_for_user_voprosi(admin.ModelAdmin):
    list_display = ('test_for_user_id', 'user_id', 'voprose_num', 'voprosi_id', 'otvet_user', 'otvet_status')

# @admin.register(User)
# class User_list(admin.ModelAdmin):
#     list_display = ('username', 'email')
