# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Definindo a ordem e os campos que você deseja
    fieldsets = (
        (None, {'fields': ('name', 'email', 'password')}),
        ('Status', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Datas de Acesso', {'fields': ('last_login', 'date_joined')}),
        ('Permissões', {'fields': ('groups', 'user_permissions')}),
    )

    # Exibe a senha como um campo de hash
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        disabled_fields = set()

        if not is_superuser:
            disabled_fields.add('is_staff')
            disabled_fields.add('is_superuser')
            disabled_fields.add('user_permissions')
            disabled_fields.add('groups')

        for f in disabled_fields:
            if f in form.base_fields:
                form.base_fields[f].disabled = True
        return form

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        else:
            return ['is_staff', 'is_superuser', 'user_permissions', 'groups']