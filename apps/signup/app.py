import rapidsms

class App (rapidsms.app.App):
    """
    Handle registering, deregistering, and updating info for alert recipients.
    """
    def handle (self, message):
        """
        Create, delete, or update the requesting user.
        
        TODO
        """
        pass
        
        # if done:
        #   self.handled = True