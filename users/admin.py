import datetime

from django.conf import settings
from django.utils import timezone
from django.utils.html import format_html
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from farm.models import FarmUser, Farm
from .models import User
from rest_framework.authtoken.models import Token


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ('key_display', 'user', 'created', 'is_expired')
    list_filter = ('user__is_staff', 'created')
    search_fields = ('user__username', 'user__email', 'key')
    readonly_fields = ('key', 'created', 'is_expired')

    def key_display(self, obj):
        return format_html("<strong>{}...</strong>", obj.key[:8])

    key_display.short_description = 'Chave do Token'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

    def is_expired(self, obj):
        token_validity_days = getattr(settings, 'TOKEN_EXPIRATION_DAYS', 7)

        expiration_date = obj.created + datetime.timedelta(days=token_validity_days)

        if timezone.now() > expiration_date:
            return format_html('<span style="color:red; font-weight: bold;">Expirado</span>')
        else:
            return format_html('<span style="color:green; font-weight: bold;">Ativo</span>')

    is_expired.short_description = 'Status de Expiração'


class FarmUserInline(admin.TabularInline):
    model = FarmUser
    extra = 1
    verbose_name = "Fazenda Associada"
    verbose_name_plural = "Fazendas Associadas"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "farm":
            if not request.user.is_superuser:
                farms_ids = request.user.farms.values_list('id', flat=True)
                kwargs["queryset"] = Farm.objects.filter(id__in=farms_ids)
            else:
                kwargs["queryset"] = Farm.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)



@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [FarmUserInline]

    fieldsets = (
        (None, {'fields': ('name', 'email', 'password')}),
        ('Status', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Datas de Acesso', {'fields': ('last_login', 'date_joined')}),
        ('Permissões', {'fields': ('groups', 'user_permissions')}),
    )

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
            return ['last_login', 'date_joined']
        else:
            return ['is_staff', 'is_superuser', 'user_permissions', 'groups', 'last_login', 'date_joined']

    list_display = ('name', 'email', 'is_active', 'is_staff', 'get_farms')

    def get_farms(self, obj):
        return ", ".join([farm.name for farm in obj.farms.all()])

    get_farms.short_description = 'Fazendas'
