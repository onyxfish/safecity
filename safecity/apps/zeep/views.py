from datetime import datetime
import logging
log = logging.getLogger("safecity.zeep.views")

from django.http import HttpResponse

from safecity.apps.locate.location_parser import *
from safecity.apps.signup.models import Resident
from safecity.apps.zeep.models import JoinSession
from safecity.apps.zeep.zeeplib import ZeepIncomingMessage

ZEEP_KEYWORD = 'safecity'

UPDATE_KEYWORDS = ('update',)

class ZeepUnexpectedEventException(Exception):
    pass

class ZeepOkResponse(HttpResponse):
    def __init__():
        super(self, HttpResponse).__init__(status=200, content_type='text/plain')

def incoming(request):
    """
    Parse an incoming message from Zeep and issue any appropriate responses.
    
    TODO: how does Zeep handle 'unjoin'?
    TODO: validate signature of messages from Zeep
    """
    #signature = request.META.get('Authorization')
    
    message = ZeepIncomingMessage(
        sender=request.POST.get('uid', None),
        text=request.POST.get('body', None),
        received=datetime.now())
    
    # Handle processes that don't require location
    event = request.POST.get('event', None)
    
    if event == 'SUBSCRIPTION_UPDATE':
        return process_join(message)   # TODO - should be processed off process?
   
    # All other messages are expected to be "mobile originated"
    if event != 'MO':
        raise ZeepUnexpectedEventException('Event was: "%s"' % event)
   
    # Annotate location
    try:
        message.parse_location()
    except NoLocationException:
        message.respond('We were unable to determine your location. Try rephrasing your message using cross-streets.')
        return ZeepOkResponse()
    except MultiplePossibleLocationsException:
        message.respond('We were unable to determine your exact location. Try providing more information, such as the block number.')
        return ZeepOkResponse()
    except RoadWithoutBlockException:
        message.respond('We were unable to determine your exact location. When stating a street name please include the block number.')
        return ZeepOkResponse()
    
    # Handle processes that do require location
    if message.sender in JoinSession.objects.all().values('phone_number'):
        return process_first_location(message)

    keyword = text.split()[0].lower()

    if keyword in UPDATE_KEYWORDS:
        return process_update(message)
        
        return process_report(message)
        
def process_join(message):
    """
    Process setting up a record of a new user and request that they establish
    their location.
    """
    # TODO: check if user already exists
    
    JoinSession.objects.create(
        phone_number=message.sender)
        
    message.respond('Thank you for joining. Reply with the word "safecity" your location to complete your signup.')
    
    return ZeepOkResponse() 
    
# def process_quit(message):
#     """
#     Process unregistering a resident.
#     """
#     Resident.objects.get(phone_number=message.sender).delete()
#     
#     # TODO - wording.... is this response even possible?
#     message.respond('You have been removed from our system and will no longer get text messages.')
#     
#     return ZeepOkResponse()

def process_first_location(message):
    """
    Process establishing a resident's initial location.
    """
    JoinSession.objects.get(phone_number=message.sender).delete()

    resident = Resident.objects.create(
        phone_number=message.sender,
        location=message.location.location)
    
    # TODO - wording
    message.respond('Thank you for registering. You will now receive messages for your area.')
    
    return ZeepOkResponse()
    
def process_update(message):
    """
    Process updating a resident's location.
    """
    resident = Resident.objects.get(phone_number=message.sender)
    resident.location = message.location.location
    resident.save()
    
    # TODO - wording
    message.respond('Thank you. Your location has been updated.')
    
    return ZeepOkResponse()
    
def process_report(message):
    """
    Process a message with no keyword--that is, a danger report.
    """     
    report = Report.objects.create(
        location=message.location.location,
        text=message.text,
        sender=message.sender,
        received=message.received)
    
    residents = report.find_nearby_residents()
    
    log.debug('Broadcasting to %i residents.' % len(residents))
    
    message.forward(
        recipients=[r for r in residents if r.phone_number != message.sender]
        )
        
    return ZeepOkResponse()