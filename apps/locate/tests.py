from django.contrib.gis.geos import Point
from rapidsms.tests.scripted import TestScript

from locate.app import *

class TestApp(TestScript):
    """
    Test locate app.
    
    TODO: find better locations for test cases
    """
    apps = (App,)
    fixtures = []
    
    # Test locations
    TROUT_AND_STUART = Point(-88.262078, 42.062726)
    N_ELMA_AND_FIRST = Point(-88.262678, 42.060726)
    STEWART_AND_VICTOR = Point(-88.258378, 42.062826)
    TWELVE_HUNDRED_TROUT = Point(-88.262178, 42.061926)
    
    def testExtractIncompleteInfo(self):
        test_messages = {
            # Incomplete info
            '': None,
            'There is no location in this message.': None,
            'This message just has a street; Augusta.': None,
        }
        
        for message, location in test_messages.items():
            print 'Testing: "%s"' % message
            self.assertEqual(extract_location(message), location)
            
    def testExtractIntersection(self):
        test_messages = {
            'Trout & Stuart': self.TROUT_AND_STUART,
            'Stuart & Trout': self.TROUT_AND_STUART,
            'Trout and Stuart': self.TROUT_AND_STUART,
            'Trout/Stuart': self.TROUT_AND_STUART,
            'Corner of Trout and Stuart': self.TROUT_AND_STUART,
            'On Trout near Stuart Ave': self.TROUT_AND_STUART,
            'Trout Ave and Stuart Ave': self.TROUT_AND_STUART,
            'Elma and 1st': None, # Elma is ambigous
            'N Elma and 1st': self.N_ELMA_AND_FIRST,
            'Something is happening at Trout and Stuart': self.TROUT_AND_STUART,
            'They are at the corner of Trout and Stuart': self.TROUT_AND_STUART,
        }

        for message, location in test_messages.items():
            print 'Testing: "%s"' % message
            self.assertEqual(extract_location(message), location)
        
    def testExtractBlock(self):
        test_messages = {
            '1200 Trout': self.TWELVE_HUNDRED_TROUT,
            '1200 Trout Ave': self.TWELVE_HUNDRED_TROUT,
            '1200 block of Trout Ave': self.TWELVE_HUNDRED_TROUT,
            '1227 Trout': self.TWELVE_HUNDRED_TROUT,
        }

        for message, location in test_messages.items():
            print 'Testing: "%s"' % message
            self.assertEqual(extract_location(message), location)
        
    def testExtractEdgeCases(self):
        test_messages = {
            'N Trout and Stuart': self.TROUT_AND_STUART, # There is no N Trout, just Trout
            '1200 N Trout': self.TWELVE_HUNDRED_TROUT, # see previous
            'Trout St and Stuart': self.TROUT_AND_STUART, # Trout is an Ave, not a St
            #'Trout, Stuart, and Victor': ?, # 3 roads
            #'X between Y and Z': ?,
            #'N X and Y': ?, # N X doesn't intersect Y, but S X does
        }

        for message, location in test_messages.items():
            print 'Testing: "%s"' % message
            self.assertEqual(extract_location(message), location)
            