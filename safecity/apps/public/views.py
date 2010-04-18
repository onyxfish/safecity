import logging
log = logging.getLogger("safecity.public.views")

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response

from safecity.apps.danger.models import Report

def index(request):
    """
    Render the index page that displays anonymized data for public
    consumption.
    """
    context = {
        'settings': settings,
    }
    
    return render_to_response(
        'public/index.html',
        context)