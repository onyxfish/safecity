from django.contrib import admin

from apps.logger.models import OutgoingMessage, IncomingMessage

admin.site.register(OutgoingMessage)
admin.site.register(IncomingMessage)
