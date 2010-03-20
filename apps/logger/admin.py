from django.contrib import admin

from logger.models import OutgoingMessage, IncomingMessage

admin.site.register(OutgoingMessage)
admin.site.register(IncomingMessage)
