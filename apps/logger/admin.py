from django.contrib import admin

from apps.logger.models import OutgoingMessage, IncomingMessage

class OutgoingMessageAdmin(admin.ModelAdmin):
    # Basic admin config
    date_hierarchy = 'sent'
    fields = ('identity', 'text', 'backend')
    list_display = ('sent', 'identity', 'backend', 'text')
    readonly_fields = ('identity', 'text', 'backend')
    search_fields = ('=identity', 'text')
    
class IncomingMessageAdmin(admin.ModelAdmin):
    # Basic admin config
    date_hierarchy = 'received'
    fields = ('identity', 'text', 'backend')
    list_display = ('received', 'identity', 'backend', 'text')
    readonly_fields = ('identity', 'text', 'backend')
    search_fields = ('=identity', 'text')

admin.site.register(OutgoingMessage, OutgoingMessageAdmin)
admin.site.register(IncomingMessage, IncomingMessageAdmin)
