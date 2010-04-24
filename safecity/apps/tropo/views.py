from datetime import datetime
import logging
log = logging.getLogger("safecity.tropo.views")

from safecity.apps.danger.models import Report
from safecity.apps.locate.location_parser import *
from safecity.apps.signup.models import Resident
from safecity.apps.tropo.tropolib import *
from safecity.lib.messages import *

def incoming(request):
    """
    Process incoming messages from Tropo.
    """
    message = TropoIncomingMessage(
        sender=request.REQUEST.get('sender'),
        text=str(request.REQUEST.get('text')),
        received=datetime.now())
    
    # TODO - strip whitespace
    # TODO - handle blank messages
    
    keyword = message.text.split()[0].lower()
       
    # Annotate location
    try:
        message.parse_location()
    except NoLocationException:
        message.respond('We were unable to determine your location. Try rephrasing your message using cross-streets.')
        return TropoOkResponse()
    except MultiplePossibleLocationsException:
        message.respond('We were unable to determine your exact location. Try providing more information, such as the block number.')
        return TropoOkResponse()
    except RoadWithoutBlockException:
        message.respond('We were unable to determine your exact location. When stating a street name please include the block number.')
        return TropoOkResponse()
    
    if keyword == 'join':
        return process_join(message)   # TODO - should be processed off process?
    elif keyword == 'update':
        return process_update(message)

    return process_report(message)
    
def process_join(message):
    """
    Process setting up a record of a new user and request that they establish
    their location.
    """
    try:
        Resident.objects.get(phone_number=message.sender)
        message.respond('You have already joined Safecity. To change your location text "update" and where you are.')
        return TropoOkResponse()
    except Resident.DoesNotExist:
        resident = Resident.objects.create(
            phone_number=message.sender,
            location=message.location.location)
        
    message.respond('Thank you for registering. You will now receive messages for your area.')

    return TropoOkResponse()

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

def process_update(message):
    """
    Process updating a resident's location.
    """
    resident = Resident.objects.get(phone_number=message.sender)
    resident.location = message.location.location
    resident.save()

    # TODO - wording
    message.respond('Thank you. Your location has been updated.')
    
    return TropoOkResponse()

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
            recipients=[r.phone_number for r in recipients]
            )

    return TropoOkResponse()