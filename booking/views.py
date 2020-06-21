import datetime

from djmoney.contrib.exchange.backends import OpenExchangeRatesBackend
from djmoney.contrib.exchange.models import convert_money
from djmoney.money import Money

from django.views import View
from django.http import HttpResponse, JsonResponse
from django.db import transaction, IntegrityError
from django.db.models import Sum, Avg
from django.core.mail import send_mail

from codebnb.utils import check_user_status, calculate_discounts, login_required
from codebnb.settings import OPEN_EXCHANGE_RATES_URL, EMAIL_HOST_USER
from room.models import Room
from user.models import User, UserProfile, LoginInfo, LoginPlatform
from review.models import Review
from booking.models import Booking, Currency, PaymentMethod
from .models import *

class BookingView(View):
    @check_user_status
    def get(self, request):
        user            = request.user
        room_id         = request.GET.get('room_id', None)
        currency        = request.GET.get('display_currency', None)
        check_in        = request.GET.get('checkin')
        check_in_date   = datetime.datetime.strptime(check_in, '%Y-%m-%d')
        check_out       = request.GET.get('checkout')
        check_out_date  = datetime.datetime.strptime(check_out, '%Y-%m-%d') if check_out else None
        guests_total    = request.GET.get('guests') 
        room = Room.objects.prefetch_related(
            'bedroom_set',
            'bath_set',
            'review_set',
            'roomimage_set'
            ).get(id=room_id)
        
        user_currency = UserProfile.objects.get(user=user).currency.name if user else "USD"
        price = room.price
        if currency:
            backend        = OpenExchangeRatesBackend(OPEN_EXCHANGE_RATES_URL)
            price_currency = convert_money(Money(room.price, user_currency), currency)
            price_split    = str(price_currency).replace(',', '').split(' ')
            price          = str(int(float(price_split[0]))) + " " + price_split[1]

        num_beds = 0
        for bedroom in room.bedroom_set.all():
            num_beds += bedroom.bed_set.aggregate(Sum('quantity'))['quantity__sum']
        ratings_dict = room.review_set.aggregate(\
                *[Avg(field) for field in ['rating__cleanliness', 'rating__communication', \
                   'rating__check_in', 'rating__accuracy', 'rating__location', 'rating__value']])
        overall_rating = 0 if None in ratings_dict.values() else sum(ratings_dict.values())/6
        
        booking_information = {
            'room_id'         : room.id,
            'title'           : room.title,
            'room_picture'    : room.roomimage_set.values_list('image_url', flat=True)[0], 
            'check_in_time'   : room.check_in.strftime("%-I:%M"),
            'check_out_time'  : room.check_out.strftime("%-I:%M"), 
            'check_in_date'   : check_in,
            'check_out_date'  : check_out,
            'place_type'      : room.place_type.name,
            'guests_total'    : guests_total,
            'bedrooms'        : room.bedroom_set.count(),
            'beds'            : num_beds,
            'baths'           : room.bath_set.count(),
            'currency'        : currency if currency else user_currency,
            'price'           : price,
            'discount_rate'   : calculate_discounts(room, check_in_date, check_out_date),
            'rules'           : room.rules,
            'overall_rating'  : overall_rating,
            'num_reviews'     : room.review_set.count(),
            'host_name'       : room.host.fullname,
            'host_avatar'     : room.host.profile.avatar_image,
            'profile_header'  : room.host.profile.profile_header,
            'user_since'      : room.host.created_at.strftime("%Y"),
            'payment_methods' : list(PaymentMethod.objects.values_list('name', flat=True))
        }
        return JsonResponse({'booking_information':booking_information}, status=200)
    
    @login_required
    def post(self, request):
        try:
            user            = request.user
            data            = json.loads(request.body)
            room_id         = data['room_id']
            room            = Room.objects.get(id=room_id)
            greeting        = data['greeting']
            start_date      = datetime.datetime.strptime(data['check_in'], '%Y-%m-%d')
            end_date        = datetime.datetime.strptime(data['check_out'], '%Y-%m-%d')
            adults          = data['adults']
            children        = data['children']
            infants         = data['infants']
            total_cost      = data['total_cost']
            payment_method  = data['payment_method']
            
            with transaction.atomic():
                Booking.objects.create(
                    user            = user,
                    room            = room,
                    payment_method  = PaymentMethod.objects.get(name=payment_method),
                    trip_status     = BookingStatus.objects.get(name='upcoming'),
                    start_date      = start_date,
                    end_date        = end_date,
                    final_price     = total_cost,
                    adults          = adults,
                    children        = children,
                    infants         = infants
                )
                user_email = LoginInfo.objects.filter(user=user).first().email
                send_mail(
                    '예약이 확정되었습니다.',
                    f'{user.fullname} 님의 예약 호스트는 {room.host.fullname} 님입니다. \n \
                    {room.host.fullname} 님에게 연락하여 도착 시간과 체크인 방법에 대해 논의하세요. \n \
                    궁금한 사항은 전 세계 모든 노마드 코더들을 위해 연중무휴 24시간 서비스를 제공하는 코드비엔비 지원팀에 연락주세요.',
                    EMAIL_HOST_USER,
                    [f'{user_email}'],
                    fail_silently=False
                )
            return HttpResponse(status=200)
        except KeyError:
            return JsonResponse({'error':'INVALID_KEY'}, status=400)
        except IntegrityError:
            return JsonResponse({'error':'TRANSACTION_FAILURE'}, status=400)
        except PaymentMethod.DoesNotExist:
            return JsonResponse({'error':'INVALID_PAYMENT'}, status=404)
        except Room.DoesNotExist:
            return JsonResponse({'error':'ROOM_NOT_FOUND'}, status=404)

