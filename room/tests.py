import json
import datetime

from .models import (
    Room, RoomAmenity, RoomCharacteristic, RoomSafetyFacility, RoomSharedSpace, 
    PlaceType, PropertyType 
)
from user.models import User, UserProfile
from django.test import TestCase, Client
from unittest.mock import patch, MagicMock

class ListTest(TestCase):
    @classmethod
    def setUp(self):
        apartment = PropertyType(
            name = '아파트'
        )
        apartment.save()
        private = PlaceType(
            name = '개인실'
        )
        private.save()
        profile = UserProfile(
            profile_header = "hi"
        )
        profile.save()
        user = User(
            username = 'junepyo',
            fullname = 'junepyo',
            is_host  = True,
            profile  = profile
        )
        user.save()
        room = Room(
            title            = "World's best house for nomad coders",
            address          = "Gangnam-gu, 서울, 대한민국",
            description      = "5G internet, complimentary thunderbolt cables, 3 minutes walk to Seonleung station,\
                house equipment include iMac, 16-inch MacBook pro, and Keychron wireless mechanical keyboard.",
            price            = 130.00,
            max_capacity     = 4,
            host             = user,
            check_in         = datetime.time(15-00-00),
            check_out        = datetime.time(12-00-00),
            latitude         = 37.501670,
            longitude        = 127.035530,
            monthly_stay     = True,
            place_type       = private,
            property_type    = apartment
        )
        room.save()

    def tearDown(self):
        Room.objects.all().delete()
        PropertyType.objects.all().delete()
        PlaceType.objects.all().delete()
        UserProfile.objects.all().delete()

    def test_roomlistview_get_success(self):
        client = Client()
        response = client.get('/room/list?location=서울&limit=10&offset=0')

        self.assertEqual(response.json()['rooms'][0]['title'], "World's best house for nomad coders")
        self.assertEqual(response.status_code, 200)
    
    def test_roomlistview_get_not_found(self):
        client = Client()
        response = client.get('/room/lists?location=서울')
        self.assertEqual(response.status_code, 404)

class DetailTest(TestCase):
    def setUp(self):
        apartment = PropertyType(
            name = '아파트'
        )
        apartment.save()
        private = PlaceType(
            name = '개인실'
        )
        private.save()
        profile = UserProfile(
            profile_header = "hi"
        )
        profile.save()
        user = User(
            username = 'junepyo',
            fullname = 'junepyo',
            is_host  = True,
            profile  = profile
        )
        user.save()
        room = Room(
            title            = "World's best house for nomad coders",
            address          = "Gangnam-gu, 서울, 대한민국",
            description      = "5G internet, complimentary thunderbolt cables, 3 minutes walk to Seonleung station,\
                house equipment include iMac, 16-inch MacBook pro, and Keychron wireless mechanical keyboard.",
            price            = 130.00,
            host             = user,
            max_capacity     = 4,
            check_in         = datetime.time(15-00-00),
            check_out        = datetime.time(12-00-00),
            latitude         = 37.501670,
            longitude        = 127.035530,
            monthly_stay     = True,
            place_type       = private,
            property_type    = apartment
        )
        room.save()

    def tearDown(self):
        Room.objects.all().delete()
        PropertyType.objects.all().delete()
        PlaceType.objects.all().delete()
        UserProfile.objects.all().delete()

    def test_roomdetailview_get_success(self):
        client = Client()
        room_id = Room.objects.all().first().id
        response = client.get(f'/room/detail/{room_id}')
        self.assertEqual(response.json()['room_info']['title'], "World's best house for nomad coders") 
        self.assertEqual(response.status_code, 200)

    def test_roomdetailview_get_fail(self):
        client = Client()
        response = client.get('/room/detail/225')
        self.assertEqual(response.json(),
            {
                'error':'ROOM_NOT_FOUND'
            }
        )
        self.assertEqual(response.status_code, 404)
    
    def test_roomdetailview_get_not_found(self):
        client = Client()
        response = client.get('room/details/2')
        self.assertEqual(response.status_code, 404)