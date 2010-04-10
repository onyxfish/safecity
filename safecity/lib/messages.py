from safecity.apps.locate.location_parser import LocationParser

LOCATION_PARSER = LocationParser()

class OutgoingMessage(object):
    """
    Helper class for outgoing messages.

    Expected to be overriden by specific backends.
    """
    def __init__(self, recipients=[], text=''):
        self.recipients = recipients
        self.text = text
        self.sent = None

    def send(self):
        """
        Send this message, should be overridden by subclasses.
        """
        self.sent = datetime.now()

class IncomingMessage(object):
    """
    Helper class for incoming messages.
    """
    def __init__(self, sender, text, received, outgoing_cls=OutgoingMessage):
        self.sender = sender
        self.text = text
        self.received = received
        self.outgoing_cls=outgoing_cls
        self.location = None
        
    def parse_location(self):
        self.location = LOCATION_PARSER.extract_location(self.text)
        
    def respond(self, text):
        self.outgoing_cls(self.sender, text).send()
        
    def forward(self, recipients):
        self.outgoing_cls(recipients, self.text).send()