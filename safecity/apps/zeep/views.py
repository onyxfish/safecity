from datetime import datetime
import logging
log = logging.getLogger("safecity.zeep.views")

from safecity.apps.danger.models import Report
from safecity.apps.locate.location_parser import *
from safecity.apps.signup.models import Resident
from safecity.apps.zeep.models import JoinSession
from safecity.apps.zeep.zeeplib import *

ZEEP_KEYWORD = 'safecity'

UPDATE_KEYWORDS = ('update',)

def incoming(request):
    """
    Parse an incoming message from Zeep and issue any appropriate responses.
    
    TODO: how does Zeep handle 'unjoin'?
    TODO: validate signature of messages from Zeep
    """
    #signature = request.META.get('Authorization')
    
    message = ZeepIncomingMessage(
        sender=request.POST.get('uid', None),
        text=str(request.POST.get('body', None)),   # NOTE: no Unicode support
        received=datetime.now())
    
    # Handle processes that don't require location
    event = request.POST.get('event', None)
    
    log.info(message.sender)
    log.info(event)
    
    if event == 'SUBSCRIPTION_UPDATE':
        return process_join(message)   # TODO - should be processed off process?
    
    # All other messages are expected to be "mobile originated"
    if event != 'MO':
        raise ZeepUnexpectedEventException('Event was: "%s"' % event)
   
    # Annotate location
    try:
        message.parse_location()
    except NoLocationException:
        return ZeepReplyResponse('We were unable to determine your location. Try rephrasing your message using cross-streets.')
    except MultiplePossibleLocationsException:
        return ZeepReplyResponse('We were unable to determine your exact location. Try providing more information, such as the block number.')
    except RoadWithoutBlockException:
        return ZeepReplyResponse('We were unable to determine your exact location. When stating a street name please include the block number.')
    
    # Handle processes that do require location
    try:
        JoinSession.objects.get(phone_number=message.sender)
        return process_first_location(message)
    except:
        pass

    keyword = message.text.split()[0].lower()

    if keyword in UPDATE_KEYWORDS:
        return process_update(message)
        
    return process_report(message)
        
def process_join(message):
    """
    Process setting up a record of a new user and request that they establish
    their location.
    """
    try:
        Resident.objects.get(phone_number=message.sender)
        return ZeepReplyResponse('You have already joined Safecity. To change your location text "safecity update" and where you are.')
    except Resident.DoesNotExist:
        pass
        
    try:
        JoinSession.objects.get(phone_number=message.sender)
        return ZeepReplyResponse('Reply to this message wtih the word "safecity" and your location.')
    except JoinSession.DoesNotExist:
        pass
    
    JoinSession.objects.create(
        phone_number=message.sender)
    
    return ZeepReplyResponse('Thank you for joining. To finish joining reply to this message with the word "safecity" and your location.')
    
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
    
    return ZeepReplyResponse('Thank you for registering. You will now receive messages for your area.')
    
def process_update(message):
    """
    Process updating a resident's location.
    """
    resident = Resident.objects.get(phone_number=message.sender)
    resident.location = message.location.location
    resident.save()
    
    # TODO - wording
    return ZeepReplyResponse('Thank you. Your location has been updated.')
    
def process_report(message):
    """
    Process a message with no keyword--that is, a danger report.
    """     
    report = Report.objects.create(
        location=message.location.location,
        text=message.text,
        sender=message.sender,
        received=message.received)
    
    recipients = report.find_nearby_residents().exclude(phone_number=message.sender)
    
    if recipients:
        log.debug('Broadcasting to %i residents.' % len(recipients))
    
        message.forward(
            recipients=recipients
            )
        
    return ZeepOkResponse()