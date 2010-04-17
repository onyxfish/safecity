from django.contrib import admin

from safecity.apps.zeep.models import *

class JoinSessionAdmin(admin.ModelAdmin):
    # Basic admin config
    fields = ('phone_number', 'datetime')
    readonly_fields = ('phone_number', 'datetime')
    search_fields = ('=phone_number',)

admin.site.register(JoinSession, JoinSessionAdmin)