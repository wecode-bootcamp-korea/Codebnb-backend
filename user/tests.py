import json
import datetime

from django.test import TestCase, Client
from unittest.mock import patch, MagicMock

from .models import User, UserProfile, LoginInfo, LoginPlatform
from booking.models import Booking, Currency
class FacebookLoginTest(TestCase):
    @classmethod
    def setUp(self):
        currency = Currency.objects.create(name='USD')
        google = LoginPlatform.objects.create(name='Google')
        facebook = LoginPlatform.objects.create(name='Facebook')

        profile = UserProfile(
            profile_header  = "Hello, I am JunePyo",
            currency     = currency,
        )
        profile.save()
        user = User(
            id          = '12345',
            username    = 'JunePyo',
            fullname    = 'JunePyo Suh',
            profile     = profile,
            birthdate   = datetime.date(1995, 11, 11)
        )
        user.save()
        LoginInfo.objects.create(
            platform    = facebook,
            user        = user,
            email       = 'june@naver.com'
        )

        profile2 = UserProfile(
            profile_header  = "Hello, I am JaeCheon",
            currency     = currency,
        )
        profile2.save()
        user2 = User(
            id          = '12346',
            username    = 'JaeCheon',
            fullname    = 'JaeCheon Song',
            profile     = profile2,
            birthdate   = datetime.date(1995, 11, 11)
        )
        user2.save()
        LoginInfo.objects.create(
            platform    = google,
            user        = user2,
            email       = 'jae@naver.com'
        )
    
    def tearDown(self):
        User.objects.all().delete()
        LoginInfo.objects.all().delete()
        UserProfile.objects.all().delete()
        Currency.objects.all().delete()
    
    @patch('user.views.requests')
    def test_user_facebook_login_success(self, mocked_requests):
        client = Client()

        class MockedResponse:
            def json(self):
                return {
                    'id'          : '12345',
                    'name'        : 'JunePyo Suh',
                    'first_name'  : 'JunePyo',
                    'email'       : 'june@naver.com',
                    'gender'      : 'male',
                    'birthday'    : '1995-08-11'
                }
        mocked_requests.get = MagicMock(return_value=MockedResponse())
        response = client.post("/user/facebook", **{"HTTP_Authorization":"1234", "content_type":"application/json"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),{
                "Authorization": response.json()['Authorization']
            }
        )
    
    @patch('user.views.requests')
    def test_user_facebook_login_fail(self, mocked_requests):
        client = Client()

        class MockedResponse:
            def json(self):
                return {
                    'id'          : '12346',
                    'name'        : 'JaeCheon Song',
                    'first_name'  : 'JaeCheon',
                    'email'       : 'jae@naver.com',
                    'gender'      : 'male',
                    'birthday'    : '1995-08-11'
                }
        mocked_requests.get = MagicMock(return_value=MockedResponse())
        response = client.post("/user/facebook", **{"HTTP_Authorization":"1234", "content_type":"application/json"})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(), {
                "message": "EXISTING_USER_GOOGLE"
            }
        )