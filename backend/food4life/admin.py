from django.contrib import admin
from .models import User

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm


class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class UserAdmin(BaseUserAdmin):
    form = MyUserChangeForm

    ordering = ('email',)
    fieldsets = None
    fields = ('email', 'first_name', 'last_name', 'password', 'is_staff', 'is_superuser', 'is_active', 'date_joined',
              'last_login', 'groups', 'user_permissions',)


admin.site.register(User, UserAdmin)
