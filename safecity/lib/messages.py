from safecity.apps.locate.location_parser import LocationParser

LOCATION_PARSER = LocationParser()

class IncomingMessage(object):
    """
    Helper class for incoming messages.
    """
    def __init__(sender, text, received, outgoing_cls=OutgoingMessage):
        self.sender = sender
        self.text = text
        self.received = received
        self.outgoing_cls=outgoing_cls
        self.location = None
        
    def parse_location():
        self.location = LOCATION_PARSER.extract_location(self.text)
        
    def respond(text):
        self.outgoing_cls(self.sender, text).send()
        
    def forward(recipients):
        self.outgoing_cls(recipients, self.text).send()
        
def OutgoingMessage(object):
    """
    Helper class for outgoing messages.
    
    Expected to be overriden by specific backends.
    """
    def __init__(recipients=[], text=''):
        self.recipients = recipients
        self.text = text
        self.sent = None
        
    def send():
        """
        Send this message, should be overridden by subclasses.
        """
        self.sent = datetime.now()