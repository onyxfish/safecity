import json
import logging
log = logging.getLogger("safecity.mock.views")

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.loader import render_to_string

from safecity.apps.tropo.views import process_message
from safecity.lib.messages import *

class MockIncomingMessage(IncomingMessage):
    """
    Back-end specific implementation of IncomingMessage.
    """
    def __init__(self, sender, text, received):
        super(MockIncomingMessage, self).__init__(
            sender, text, received)
        
        self.mock_output = []

    def respond(self, text):
        self.mock_output.append('%s <<< %s' % (self.sender, text))

    def forward(self, recipients):
        for r in recipients:
            self.mock_output.append('%s <<< %s' % (r, self.text))

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
        
@staff_member_required
def mock_sms_ajax(request):
    message = MockIncomingMessage(
        sender=request.REQUEST.get('sender'),
        text=str(request.REQUEST.get('text')),
        received=datetime.now())
        
    response = process_message(message)
    response.content = '<br />'.join(message.mock_output)
    
    return response