from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from userprofile.models import UserProfile
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from userprofile.models import *


#
# class RegisterForm(forms.Form):
#     # d = {'username': 'fyffxym', 'email': 'fyffxym@mail.ru', 'last_name': 'fyffxym', 'first_name': 'fyffxym', 'patronymic': 'fyffxym', 'password1': 'fyffxymfyffxym', 'password2': 'fyffxymfyffxym'}
#     username = forms.CharField(label=_("Логин"),
#                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Логин'}))
#     email = forms.EmailField(label=_("Email"),
#                              widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
#                              max_length=64)
#     last_name = forms.CharField(label=_("Фамилия"),
#                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}),
#                                 max_length=32)
#     first_name = forms.CharField(label=_("Имя"),
#                                  widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}),
#                                  max_length=32)
#     patronymic = forms.CharField(label=_("Отчество"),
#                                  widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Отчество'}),
#                                  max_length=32)
#
#     password1 = forms.CharField(label=_("Пароль"),
#                                 widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'}))
#     password2 = forms.CharField(label=_("Подтверждение пароля"), widget=forms.PasswordInput(
#         attrs={'class': 'form-control', 'placeholder': 'Подтверждение пароля'}))
#     class Meta:
#         model = User
#         fields = ('username', 'email', 'last_name', 'first_name', 'patronymic')
#
#
#     def clean_password2(self):
#         password1 = self.cleaned_data.get("password1")
#         password2 = self.cleaned_data.get("password2")
#         if password1 and password2 and password1 != password2:
#             raise ValidationError(
#                 self.error_messages['password_mismatch'],
#                 code='password_mismatch',
#             )
#         return password2
#
#     def clean_username(self):
#         new_username = self.cleaned_data['username'].lower()
#
#         if new_username == 'admin':
#             raise ValidationError('Данный логин нельза занимать')
#
#         if User.objects.filter(username__exact=new_username).count():
#             raise ValidationError('Данный логин занят')
#
#         return new_username
#
#     def save(self):
#         new_register = User.objects.create(
#             username=self.cleaned_data['username'],
#             email=self.cleaned_data['email'],
#             last_name=self.cleaned_data['last_name'],
#             first_name=self.cleaned_data['first_name'],
#             password=self.clean_password2
#         )
#         new_register.userprofile.patronymic = self.cleaned_data['patronymic']
#         save_user_profile(sender=new_register, instance=new_register)
#         return new_register


class SignUpForm(UserCreationForm):
    username = forms.CharField(label=_("Логин"),
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    email = forms.EmailField(label=_("Email"),
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
                             max_length=64)
    last_name = forms.CharField(label=_("Фамилия"),
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}),
                                max_length=32)
    first_name = forms.CharField(label=_("Имя"),
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}),
                                 max_length=32)
    patronymic = forms.CharField(label=_("Отчество"),
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Отчество'}),
                                 max_length=32)
    password1 = forms.CharField(label=_("Пароль"),
                                widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'}))
    password2 = forms.CharField(label=_("Подтверждение пароля"), widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Подтверждение пароля'}))

    # UserCreationForm.base_fields['password2'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = User
        fields = ('username', 'email', 'last_name', 'first_name', 'patronymic', 'password1', 'password2',)
        # widgets = {
        #     'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        #     'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
        #     'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
        #     'patronymic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
        #     'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        #     'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password', 'autocomplete': 'new-password'}),
        #     'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password Again', 'autocomplete': 'new-password'}),
        # }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2
# class SignUpForm(UserCreationForm):
#     username = forms.CharField()
#     email = forms.CharField()
#     last_name = forms.CharField()
#     first_name = forms.CharField()
#     patronymic = forms.CharField()
#     patronymic = forms.CharField(label=_("Отчество"),widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}),)
#     class Meta:
#         model = User
#         fields = ('username', 'email', 'last_name', 'first_name', 'patronymic', 'password1', 'password2',)
