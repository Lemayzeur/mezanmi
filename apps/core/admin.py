from django.contrib import admin
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('client_id', 'enabled')
    list_filter = ('enabled',)
    search_fields = ('client_id',)

    actions = ['enable_clients', 'disable_clients']

    def enable_clients(self, request, queryset):
        queryset.update(enabled=True)

    def disable_clients(self, request, queryset):
        queryset.update(enabled=False)

    enable_clients.short_description = "Enable selected clients"
    disable_clients.short_description = "Disable selected clients"
