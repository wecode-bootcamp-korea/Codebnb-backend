import jwt
import datetime

from django.http import HttpResponse, JsonResponse

from user.models import User
from room.models import Room
from booking.models import Booking
from .settings import SECRET_KEY, HASH

def login_required(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            token = request.headers.get('Authorization', None)
            user_info = jwt.decode(token, SECRET_KEY, algorithm=HASH)
            request.user = User.objects.get(id=user_info['id'])
            return func(self, request, *args, **kwargs)
        except User.DoesNotExist:
            return JsonResponse({"message" : "INVALID_USER"}, status=401)
        except jwt.exceptions.DecodeError:
            return JsonResponse({"message" : "INVALID_TOKEN"}, status=401)
    return wrapper

def check_user_status(func):
    def wrapper(self, request, *args, **kwargs):
        token = request.headers.get('Authorization', None)
        if token:
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithm = HASH)
                user_id = payload['user_id']
                request.user = User.objects.get(id=user_id)
            except jwt.DecodeError:
                return JsonResponse({"message" : "INVALID_TOKEN"}, status=401)
            except User.DoesNotExist:
                return JsonResponse({"message" : "NO_SUCH_USER"}, status=401)
            return func(self, request, *args, **kwargs)
        request.user = None
        return func(self, request, *args, **kwargs)
    return wrapper

def calculate_discounts(room, check_in_date, check_out_date):
    discount_percent = 0
    if not Booking.objects.filter(room=room):
        discount_percent += 0.1
    
    if Booking.objects.filter(room=room, created_at__lte=datetime.date.today(),\
        created_at__gt=datetime.date.today()-datetime.timedelta(days=14)):
        discount_percent += 0.1
    
    if check_in_date and check_out_date and \
        (check_out_date - check_in_date).days >= 28:
        discount_percent += 0.2
    
    return discount_percent

def first_guest_discount(room):
    return 0.05 if room.booking_set.count() == 0 else 0
       
def week_guest_discount(room, today):
    before_week = today - datetime.timedelta(days=7)
    now         = today
    return 0.05 if len(room.booking_set.filter(created_at__range = (before_week, now))) == 0 else 0
       
def monthly_stay_discount(room, start, end):
    return 0.1 if (end - start).days >= 28 and room.monthly_stay else 0