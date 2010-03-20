from rapidsms.webui.utils import render_to_response

from apps.logger.models import *

def index(request):
    """
    Display a list of logged messages
    """
    incoming = IncomingMessage.objects.order_by('received')
    outgoing = OutgoingMessage.objects.order_by('sent')

    messages = []
    messages.extend(incoming)
    messages.extend(outgoing)
    
    messages.sort(lambda x, y: cmp(y.datetime, x.datetime))
    
    return render_to_response(request, 'logger/index.html', { "messages": messages })

