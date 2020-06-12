import datetime
import json
import jwt
import requests

from django.db.models   import Q
from django.http        import HttpResponse, JsonResponse
from django.views       import View

from .models            import User, LoginInfo, UserProfile
from codebnb.settings   import SECRET_KEY, HASH
from codebnb.utils      import login_required
from codebnb.enum       import GOOGLE, FACEBOOK, MALE, FEMALE
from room.models        import RoomImage

class GoogleLoginVIew(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            access_token = data.get('access_token')
            api_request = requests.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json"     
                })
            google_info = api_request.json()
            email = google_info.get('email')
            if LoginInfo.objects.filter(email = email).exists():
                if LoginInfo.objects.filter(Q(email = email) & Q(platform_id = FACEBOOK)).exists():
                    return JsonResponse({'message': 'EXISTING_USER_FACEBOOK'}, status = 400)
                user = LoginInfo.objects.select_related('user','user__profile').get(Q(email = email) & Q(platform_id = GOOGLE))
            else:
                profile = UserProfile.objects.create()
                user = User.objects.create(username    = google_info.get('given_name'),
                                           fullname    = google_info.get('name'),
                                           profile     = profile)
                login_info = LoginInfo.objects.create(email       = email,
                                                      platform_id = GOOGLE,
                                                      user        = user)
            dic = {
                'id'        : user.user.id,
                'fullname'  : user.user.fullname,
                'username'  : user.user.username,
                'avatar'    : user.user.profile.avatar_image}
            token = jwt.encode(dic, SECRET_KEY, algorithm=HASH)
            token = token.decode('utf-8')
            return JsonResponse({'Authorization':token, 'username': dic['username'], 'avatar': dic['avatar']}, status = 200)            
        except LoginInfo.DoesNotExist:
            return HttpResponse(status = 400)

class FacebookLoginView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            access_token = data.get('access_token')
            print(access_token)
            link = f"https://graph.facebook.com/v6.0/me"
            user_info_fields = ['id', 'name', 'first_name', 'email', 'gender', 'birthday']
            user_fields = {
            'access_token'  : access_token,
            'fields'        : ','.join(user_info_fields)
            } 
            
            facebook_info = requests.get(link, params=user_fields).json()
            fullname      = facebook_info.get('name')
            first_name    = facebook_info.get('first_name')
            email         = facebook_info.get('email')
            gender        = facebook_info.get('gender')
            birthdate     = facebook_info.get('birthday')

            if LoginInfo.objects.filter(email=email, platform_id=GOOGLE).exists():
                return JsonResponse({'message': 'EXISTING_USER_GOOGLE'}, status=400)
            if LoginInfo.objects.filter(email=email).exists:
                user = LoginInfo.objects.get(email=email).user
            else:
                profile = UserProfile.objects.create(
                    profile_header = f'안녕하세요, {first_name}입니다.',
                    currency       = Currency.objects.get(name='달러'),
                    language       = Language.objects.get(name='영어(USA)')
                )
                profile.save()
                user = User(
                    username    = first_name,
                    fullname    = fullname,
                    gender      = Gender.objects.get(name=gender),
                    birthdate   = birthdate,
                    profile     = profile
                )
                user.save()
                LoginInfo.objects.create(
                    platform_id = FACEBOOK,
                    user        = user,
                    email       = email
                )
            token = jwt.encode({'user_id':user.id}, SECRET_KEY, algorithm=HASH)
            return JsonResponse({'Authorization':token.decode('utf-8')}, status=200)
        except KeyError:
            return JsonResponse({'error': 'INVALID_KEY'}, status=400)

class TripStateView(View):
    @login_required
    def get(self, request):
        user              = request.user
        today             = datetime.date.today()
        user_bookings     = User.objects.prefetch_related('booking_set', 'guest_reviews').get(id = user.id)
        up_coming_booking = user_bookings.booking_set.filter(start_date__gt = today)
        past_booking      = user_bookings.booking_set.filter(end_date__lt = today)
        booking_list = [{
            'up_coming' : [{
                'id'            : booking.id,
                'title'         : booking.room.title,
                'image_url'     : list(booking.room.roomimage_set.values_list('image_url', flat=True)[:1]),
                'start_date'    : booking.start_date,
                'end_date'      : booking.end_date,
                'address'       : booking.room.address
                } for booking in up_coming_booking.select_related('room')],
            'past_booking' : [{
                'id'            : booking.id,
                'room_id'       : booking.room.id,
                'host_id'       : booking.room.host.id,
                'title'         : booking.room.title,
                'image_url'     : list(booking.room.roomimage_set.values_list('image_url', flat=True)[:1]),
                'start_date'    : booking.start_date,
                'end_date'      : booking.end_date,
                'address'       : booking.room.address
                } for booking in past_booking.select_related('room')]}]