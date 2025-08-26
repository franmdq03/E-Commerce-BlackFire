from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account, UserProfile
from django.utils.html import format_html

class CuentaAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username', 'last_login', 'date_joined', 'is_active')
    list_display_links = ('email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('-date_joined',)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

class PerfilUsuarioAdmin(admin.ModelAdmin):
    def miniatura(self, objeto):
        if objeto.profile_picture:
            return format_html('<img src="{}" width="30" style="border-radius:50%;">', objeto.profile_picture.url)
        return '(No image)'
    miniatura.short_description = 'Foto de Perfil'

    list_display = ('miniatura', 'user', 'city', 'province', 'country')

admin.site.register(Account, CuentaAdmin)
admin.site.register(UserProfile, PerfilUsuarioAdmin)


