from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from userprofile.models import UserProfile
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from .models import test, voprosi
from django.contrib.auth.models import User

class CreateTestForm(forms.Form):
    test_name = forms.CharField(label='Название теста', max_length=50)

    def save(self):
        new_test = test.objects.create(test_name=self.cleaned_data['test_name'], create_user_id=User)
        return new_test

class CreateTestForUserForm(forms.Form):
    pass