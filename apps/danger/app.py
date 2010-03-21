import rapidsms
from rapidsms.message import Message

from apps.danger.models import Report
from apps.locate.location_parser import NoLocationException
from apps.priorities import PRIORITIES

class App(rapidsms.app.App):
    """
    This application handles receiving, parsing, and broadcasting reports of
    suspicious behavior (gang activity, etc).
    
    Depends on the "locate" app.
    """
    PRIORITY = PRIORITIES['danger']
    
    def handle (self, message):
        """
        Store the message and rebroadcast it to appropriate recipients.
        """
        if not hasattr(message, 'location') or message.location is None:
            raise NoLocationException(
                'A message without a location should not reach the danger app for processing.')
                
        report = Report.objects.create(
            location=message.location.location,
            log_entry=message.log_entry)
        
        residents = report.find_nearby_residents()
        
        self.debug('Broadcasting to %i residents.' % len(residents))
        
        for resident in residents:
            self.debug('Sending to %s' % resident.phone_number)
            message.forward(resident.phone_number)
        
        return True