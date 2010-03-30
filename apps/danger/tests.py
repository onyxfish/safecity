from datetime import datetime

from django.contrib.gis.geos import Point
from django.test import TestCase

from apps.danger.models import *
from apps.locate.models import *
from apps.signup.models import *

class TestDangerBroadcasting(TestCase):
    """
    Test the broadcasting mechanism for when new reports are received.
    """
    fixtures = [
        'data/test_fixtures/locate.Road.json', 
        'data/test_fixtures/locate.Intersection.json',
        'data/test_fixtures/locate.Block.json',
        'data/test_fixtures/signup.Resident.json',
        ]
    
    def setUp(self):
        # Roads
        self.MADISON = Road.objects.get(full_name='WEST MADISON STREET')
        self.CENTRAL = Road.objects.get(full_name='SOUTH CENTRAL AVENUE')
        self.QUINCY = Road.objects.get(full_name='WEST QUINCY STREET')
        self.LOCKWOOD = Road.objects.get(full_name='SOUTH LOCKWOOD AVENUE')
        self.HARRISON = Road.objects.get(full_name='WEST HARRISON STREET')
        self.CICERO = Road.objects.get(full_name='SOUTH CICERO AVENUE')
        
        # Northwest corner of test area
        self.MADISON_AND_CENTRAL = Intersection.find_intersection(self.MADISON, self.CENTRAL)
        
        # Center of test area
        self.QUINCY_AND_LOCKWOOD = Intersection.find_intersection(self.QUINCY, self.LOCKWOOD)
        self.FIFTY_THREE_HUNDRED_QUINCY = Block.objects.get(number=5300, road=self.QUINCY)
        
        # Southeast corner of test area
        self.HARRISON_AND_CICERO = Intersection.find_intersection(self.HARRISON, self.CICERO)
        
        # Residents
        self.NORTHWEST_RESIDENT = Resident.objects.get(phone_number='1111111111')
        self.CENTER_RESIDENT = Resident.objects.get(phone_number='2222222222')
        self.SOUTHEAST_RESIDENT = Resident.objects.get(phone_number='3333333333')
    
    def testNorthwestCorner(self):
        report = Report.objects.create(
            location=self.MADISON_AND_CENTRAL.location,
            text='Action at Madison and Central.',
            sender='1111111111',
            received=datetime.now())
            
        residents = [r.pk for r in report.find_nearby_residents()]
        
        self.assertEqual(residents, [self.NORTHWEST_RESIDENT.pk, self.CENTER_RESIDENT.pk])
    
    def testNorthWestOfCenter(self):
        report = Report.objects.create(
            location=self.QUINCY_AND_LOCKWOOD.location,
            text='Action at Quincy and Lockwood.',
            sender='2222222222',
            received=datetime.now())
            
        residents = [r.pk for r in report.find_nearby_residents()]
        
        self.assertEqual(residents, [self.NORTHWEST_RESIDENT.pk, self.CENTER_RESIDENT.pk])
        
    def testNorthWestOfCenterBlock(self):
        report = Report.objects.create(
            location=self.FIFTY_THREE_HUNDRED_QUINCY.location,
            text='Action at 5300 West Quincy.',
            sender='2222222222',
            received=datetime.now())
            
        residents = [r.pk for r in report.find_nearby_residents()]
        
        self.assertEqual(residents, [self.NORTHWEST_RESIDENT.pk, self.CENTER_RESIDENT.pk])
    
    def testSoutheastCorner(self):
        report = Report.objects.create(
            location=self.HARRISON_AND_CICERO.location,
            text='Action at Harrison and Cicero.',
            sender='3333333333',
            received=datetime.now())
            
        residents = [r.pk for r in report.find_nearby_residents()]
        
        self.assertEqual(residents, [self.SOUTHEAST_RESIDENT.pk])