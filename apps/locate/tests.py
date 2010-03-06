from rapidsms.tests.scripted import TestScript
from locate.app import *

class TestApp(TestScript):
    apps = (App,)
    
    def testExtractLocation(self):
        """
        Test extracting a location from a piece of text.
        
        TODO: add test cases and valid locations
        """
        test_messages = {
            '': None,
            'There is no location in this message.': None,
            'This message just has a street; Augusta.': None,
            'Austin & Chicago': 1234,   # TODO: need actual locations
        }
        
        for message, location in test_messages.items():
            print 'Testing: "%s"' % message
            self.assertEqual(extract_location(message), location)