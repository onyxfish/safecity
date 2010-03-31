from django.contrib.gis.geos import Point
from django.test import TestCase

from safecity.apps.locate.models import *
from safecity.apps.locate.location_parser import *

class TestLocationParser(TestCase):
    """
    Test location parser.
    """
    fixtures = [
        'data/test_fixtures/locate.Road.json', 
        'data/test_fixtures/locate.Intersection.json', 
        'data/test_fixtures/locate.Block.json'
        ]
    
    def setUp(self):
        self.parser = LocationParser()
        
        self.QUINCY = Road.objects.get(full_name='W QUINCY ST')
        self.LOCKWOOD = Road.objects.get(full_name='S LOCKWOOD AVE')
        self.QUINCY_AND_LOCKWOOD = Intersection.find_intersection(self.QUINCY, self.LOCKWOOD)
        self.FIFTY_THREE_HUNDRED_QUINCY = Block.objects.get(number=5300, road=self.QUINCY)
    
    # Missing data
    def testNoMessage(self):
        message = ''
        self.assertRaises(NoLocationException, self.parser.extract_location, message)
        
    def testNoLocation(self):
        message = 'There is no location in this message.'
        self.assertRaises(NoLocationException, self.parser.extract_location, message)
        
    def testRoadOnly(self):
        message = 'This message just has a street; Quincy.'
        self.assertRaises(RoadWithoutBlockException, self.parser.extract_location, message)
      
    # Intersections 
    def testIntersection(self):
        message = 'Quincy & Lockwood'
        self.assertEqual(self.parser.extract_location(message), self.QUINCY_AND_LOCKWOOD)
    
    def testIntersectionReverse(self):
        message = 'Lockwood & Quincy'
        self.assertEqual(self.parser.extract_location(message), self.QUINCY_AND_LOCKWOOD)
        
    def testIntersectionNoAnd(self):
        message = 'Quincy Lockwood'
        self.assertEqual(self.parser.extract_location(message), self.QUINCY_AND_LOCKWOOD)
        
    def testIntersectionAnd(self):
        message = 'Quincy and Lockwood'
        self.assertEqual(self.parser.extract_location(message), self.QUINCY_AND_LOCKWOOD)
        
    def testIntersectionNoSpace(self):
        message = 'Quincy&Lockwood'
        self.assertEqual(self.parser.extract_location(message), self.QUINCY_AND_LOCKWOOD)
        
    def testIntersectionSlash(self):
        message = 'Quincy / Lockwood'
        self.assertEqual(self.parser.extract_location(message), self.QUINCY_AND_LOCKWOOD)
        
    def testIntersectionSlashNoSpace(self):
        message = 'Quincy/Lockwood'
        self.assertEqual(self.parser.extract_location(message), self.QUINCY_AND_LOCKWOOD)
        
    def testIntersectionContext(self):
        message = 'Something is happening at Quincy and Lockwood, something really bad.'
        self.assertEqual(self.parser.extract_location(message), self.QUINCY_AND_LOCKWOOD)
        
    def testIntersectionNear(self):
        message = 'On Quincy near Lockwood'
        self.assertEqual(self.parser.extract_location(message), self.QUINCY_AND_LOCKWOOD)
        
    def testIntersectionTypes(self):
        message = 'Quincy St & Lockwood Ave'
        self.assertEqual(self.parser.extract_location(message), self.QUINCY_AND_LOCKWOOD)
        
    def testIntersectionBadTypes(self):
        message = 'Quincy Ave & Lockwood Blvd'
        self.assertEqual(self.parser.extract_location(message), self.QUINCY_AND_LOCKWOOD)
        
    def testIntersectionDirections(self):
        message = 'W Quincy & S Lockwood'
        self.assertEqual(self.parser.extract_location(message), self.QUINCY_AND_LOCKWOOD)
        
    def testIntersectionBadDirections(self):
        message = 'N Quincy St & N Lockwood Ave'
        self.assertEqual(self.parser.extract_location(message), self.QUINCY_AND_LOCKWOOD)
        
    def testIntersectionBadEverything(self):
        message = 'N Quincy Ave E & N Lockwood Pkwy W'
        self.assertEqual(self.parser.extract_location(message), self.QUINCY_AND_LOCKWOOD)
        
    # Blocks
    def testBlock(self):
        message = '5300 Quincy'
        self.assertEqual(self.parser.extract_location(message), self.FIFTY_THREE_HUNDRED_QUINCY)
        
    def testBlockHigh(self):
        message = '5399 Quincy St'
        self.assertEqual(self.parser.extract_location(message), self.FIFTY_THREE_HUNDRED_QUINCY)
        
    def testBlockLow(self):
        message = '5301 Quincy St'
        self.assertEqual(self.parser.extract_location(message), self.FIFTY_THREE_HUNDRED_QUINCY)
        
    def testBlockPrevious(self):
        message = '5299 Quincy St'
        self.assertNotEqual(self.parser.extract_location(message), self.FIFTY_THREE_HUNDRED_QUINCY)
        
    def testBlockNext(self):
        message = '5400 Quincy St'
        self.assertNotEqual(self.parser.extract_location(message), self.FIFTY_THREE_HUNDRED_QUINCY)
        
    def testBlockType(self):
        message = '5300 Quincy St'
        self.assertEqual(self.parser.extract_location(message), self.FIFTY_THREE_HUNDRED_QUINCY)
        
    def testBlockBadType(self):
        message = '5300 Quincy Ave'
        self.assertEqual(self.parser.extract_location(message), self.FIFTY_THREE_HUNDRED_QUINCY)
        
    def testBlockBadLargeNumber(self):
        message = '111000 Quincy St'
        self.assertRaises(RoadWithoutBlockException, self.parser.extract_location, message)
        
    def testBlockOf(self):
        message = '5300 block of Quincy St'
        self.assertEqual(self.parser.extract_location(message), self.FIFTY_THREE_HUNDRED_QUINCY)
        
    # Edge cases
    def testBetween(self):
        message = 'Quincy between Lotus and Lockwood'
        self.assertEqual(self.parser.extract_location(message), self.FIFTY_THREE_HUNDRED_QUINCY)
    
    def testThreeStreets(self):
        message= 'Quincy, Lotus, and Lockwood'
        self.assertEqual(self.parser.extract_location(message), self.FIFTY_THREE_HUNDRED_QUINCY)