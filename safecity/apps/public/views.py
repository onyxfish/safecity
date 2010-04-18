import logging
log = logging.getLogger("safecity.public.views")

from django.http import HttpResponse

from safecity.apps.danger.models import Report

def index(request):
    """
    Render the index page that displays anonymized data for public
    consumption.
    """
    return HttpResponse(content='TODO')