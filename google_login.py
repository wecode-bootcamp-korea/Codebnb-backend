import json
import bcrypt
import datetime

from django.test    import TestCase, Client
from unittest.mock  import patch, MagicMock

from user.models        import User, LoginPlatform, LoginInfo
from user.views         import GoogleLoginView
from booking.models     import Currency

class GoogleLoginTest(TransactionTestCase):

    def setUp(self):
        currency = Currency.objects.create(name='USD')
        google = LoginInfo.objects.create(name="Google")
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
            platform    = google,
            user        = user,
            email       = 'june@naver.com'
        )

    def tearDown(self):
        User.objects.all().delete()
        UserProfile.objects.all().delete()
        LoginInfo.objects.all().delete()
          
    @patch('user.views.requests')
    def test_user_google_login(self, mocked_requests):
        client = Client()

        class MockedResponse:
            def json(self):
                return {
                    "user_id"    : "12345",
                    "name"       : "JunePyo Suh"
                }
        
        mocked_requests.get = MagicMock(return_value = MockedResponse())
        response = client.post("/user/google", **{"HTTP_Authorization":"1234", "content_type":"application/json"})
        
        return response.json()['access_token']
