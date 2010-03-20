from datetime import datetime

import rapidsms

from apps.signup.models import Citizen

class App (rapidsms.app.App):
    """
    Handle registering, deregistering, and updating info for alert recipients.
    """
    def start(self):
        self.PROCESSORS = {
            'on': self.on,
            'register': self.on,
            'update': self.on,
            'off': self.off,
            'deregister': self.off,
            'unregister': self.off,
        }
    
    def handle (self, message):
        """
        Create, delete, or update the requesting user.
        
        When creating or updating a user this app assumes that locate has
        already annotated location information onto the message.
        """
        text = message.text.lower()
        
        for key, func in self.PROCESSORS.items():
            if text.startswith(key):
                func(message)
                return True
        
        return False
        
    def on(self, message):
        """
        Register or update user.
        """
        if not hasattr('location', message) or message.location is None:
            # TODO
            message.respond('Please include your location in your message.')
            
        try:
            resident = Resident.objects.get(phone_number=message.connection.identity)
            resident.location = message.location
            resident.save()
        except Resident.DoesNotExist:
            resident = Resident.objects.create(
                phone_number=message.connection.identity,
                location=message.location)
        
    def off(self, message):
        """
        Deregister user.
        
        For the sake of privacy users are completely deleted from the system.
        """
        try:
            resident = Resident.objects.get(phone_number=message.connection.identity)
        except Resident.DoesNotExist:
            # TODO
            message.respond('The phone number you are texting from is not in our system.')
            return
        
        resident.delete()