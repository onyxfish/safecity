import json
import logging
log = logging.getLogger("safecity.mock.views")

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.loader import render_to_string

from safecity.apps.tropo.views import incoming

@staff_member_required
def mock(request):
    """
    Create a form for mocking up SMS messages.
    """
    context = {
        'settings': settings,
    }
    
    return render_to_response(
        'mock/mock.html',
        context)