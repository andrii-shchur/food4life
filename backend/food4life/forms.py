from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']


class UploadFileForm(forms.Form):
    file = forms.FileField()
