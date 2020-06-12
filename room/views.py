import datetime 
import sys
import time

from django.views import View
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.db.models import Q, F, Count, Avg, Sum

from codebnb.utils import check_user_status, login_required, calculate_discounts, first_guest_discount, week_guest_discount, monthly_stay_discount 
from codebnb.enum import AMENITIES_LIST
from codebnb.settings import S3_ACCESS_KEY_ID, S3_SECRET_ACCESS_KEY
from .models import Room, Bedroom, Bed, RoomAmenity, RoomSharedSpace, RoomSafetyFacility, BlockedDate, Bath
from user.models import Wishlist
from review.models import Review, Rating
from booking.models import Booking

class MonthlyStayListView(View):
    @check_user_status
    def get(self, request):
        user            = request.user
        today           = datetime.date.today()
        check_in        = datetime.datetime.strptime(request.GET.get('checkin', str(today)), '%Y-%m-%d')
        check_out       = datetime.datetime.strptime(request.GET.get('checkout', str(today)), '%Y-%m-%d')
        members         = int(request.GET.get('adults', 0)) + int(request.GET.get('children', 0))
        min_cost        = float(request.GET.get('min_cost', 0))
        max_cost        = float(request.GET.get('max_cost', 1000))
        location        = request.GET.get('location', '한국')
        min_beds        = int(request.GET.get('min_beds', 0))
        min_bedrooms    = int(request.GET.get('min_bedrooms', 0))
        min_baths       = int(request.GET.get('min_baths', 0))
        amenities       = request.GET.getlist('amenities', AMENITIES_LIST)
        property_type   = request.GET.getlist('property_type', PROPERTIES)
        place_type      = request.GET.getlist('place_type',PLACES)
        languages       = request.GET.get('languages', LANGUAGES)
        monthly_stay    = bool(request.GET.get('monthly_stay', True))
        room_list       = []
        rooms           = Room.objects.select_related('host','place_type', 'property_type').prefetch_related(
            'roomamenity_set',
            'bedroom_set',
            'roomimage_set',
            'bath_set',
            'review_set',
            'blockeddate_set',
            'booking_set',
            ).filter(
                Q(address__contains = location)&
                Q(max_capacity__gte = members)&
                Q(price__range = (min_cost, max_cost))&
                Q(property_type_id__name__in = property_type)&
                Q(place_type_id__name__in = place_type)&
                Q(monthly_stay = monthly_stay)&
                Q(amenities__name__in = AMENITIES_LIST)&
                Q(bath__quantity__gte = min_baths)&
               ~Q(blockeddate__start_date__range = (check_in, check_out))&
               ~Q(blockeddate__end_date__range = (check_in, check_out))&
               ~Q(booking__start_date__range = (check_in, check_out))&
               ~Q(booking__end_date__range = (check_in, check_out))).distinct()
        if len(rooms) == 0:
            return JsonResponse({'message':'DoesNotExist Filter Room LIst'}, status = 200)
        for room in rooms:
            total_bed = 0
            bedrooms = room.bedroom_set.all()
            if len(bedrooms) < min_bedrooms:
                continue
            if not room.host.userlanguage_set.filter(language_id__name__in = languages).exists():
                continue
            for bedroom in bedrooms:
                bed = bedroom.bed_set.values('quantity')
                total_bed += bed[0]['quantity']
            if total_bed < min_beds:
                continue
            reviews   = room.review_set.all()
            ratings   = 0
            for review in reviews:
                ratings += (review.rating.cleanliness + review.rating.communication + review.rating.check_in + 
                            review.rating.accuracy + review.rating.location+ review.rating.value)/6
            discount  = first_guest_discount(room) + week_guest_discount(room, today) + monthly_stay_discount(room, check_in, check_out)
            room_dic = {
                'id'            : room.id,
                'title'         : room.title,
                'images'        : list(room.roomimage_set.values_list('image_url', flat=True)),
                'bedrooms'      : len(bedrooms),
                'beds'          : total_bed,
                'baths'         : len(room.bath_set.all()),
                'max_capacity'  : room.max_capacity,
                'address'       : room.address,
                'latitude'      : room.latitude ,
                'longitude'     : room.longitude ,
                'features'      : list(room.amenities.values_list('name', flat=True)[:3]),
                'property_type' : room.property_type.name,
                'place_type'    : room.place_type.name,
                'price'         : room.price,
                'discount_rate' : discount,
                'reviews'       : len(reviews),
                'rating'        : float(ratings/len(reviews)) if len(reviews) != 0 else 0,
                'is_wishlist'   : True if user and Wishlist.objects.filter(room=room, user=user).exists() else False}
            room_list.append(room_dic)
        room_list.append({'total_rooms' : len(rooms)})
        return JsonResponse({'data':room_list}, status = 200)

class RoomListView(View):
    def list_q(self, queries, field, values):
        for value in values:
            queries &= Q(**{field: value})
        return queries
    
    def annotation_filter(self, qs, name, aggregation, op, value):
        if value:
            return qs.annotate(**{name: aggregation}).filter(
                **{f"{name}__{op}": value}
            )
        return qs

    @check_user_status
    def get(self, request):
        user            = request.user
        limit           = int(request.GET.get('limit'))
        offset          = int(request.GET.get('offset'))
        location        = request.GET.get('location')
        adults          = int(request.GET.get('adults', 0))
        children        = int(request.GET.get('children', 0))
        infants         = request.GET.get('infants', 0)
        min_cost        = float(request.GET.get('min_cost', 0))
        max_cost        = float(request.GET.get('max_cost', sys.maxsize))
        property_type   = request.GET.get('property_type', None)
        place_type      = request.GET.get('place_type', None)
        check_in        = request.GET.get('checkin', None)
        check_in_date   = datetime.datetime.strptime(check_in, '%Y-%m-%d') if check_in else None
        check_out       = request.GET.get('checkout', None)
        check_out_date  = datetime.datetime.strptime(check_out, '%Y-%m-%d') if check_out else None
        min_beds        = request.GET.get('min_beds', None)
        min_bedrooms    = request.GET.get('min_bedrooms', None)
        min_baths       = request.GET.get('min_baths', None)
        amenities       = request.GET.getlist('amenities', None)
        languages       = request.GET.getlist('languages', None)
        
        print(location)
        queries = (
            Q(address__icontains = location) 
            & Q(max_capacity__gte = adults + children)
            & Q(price__range = (min_cost, max_cost))
        )
        if check_in_date and check_out_date:
            queries &= (
                ~Q(blockeddate__start_date__range = (check_in_date, check_out_date)) 
                & ~Q(blockeddate__end_date__range = (check_in_date, check_out_date)) 
                & ~Q(booking__start_date__range = (check_in_date, check_out_date)) 
                & ~Q(booking__end_date__range = (check_in_date, check_out_date))
            )
        if property_type:
            queries &= Q(property_type__name = property_type)
        if place_type:
            queries &= Q(place_type__name = place_type)
        queries = self.list_q(queries, "amenities__name", amenities)
        queries = self.list_q(queries, "host__userlanguage__language__name", languages)
        print(queries)
        room_qs = Room.objects.filter(queries)

        room_qs = self.annotation_filter(room_qs, "num_beds", Sum("bedroom__bed__quantity"), "gte", min_beds)
        room_qs = self.annotation_filter(room_qs, "num_bedrooms", Count("bedroom"), "gte", min_bedrooms)
        room_qs = self.annotation_filter(room_qs, "num_baths", Count("bath"), "gte", min_baths)
        room_qs = room_qs.order_by('id')[offset:offset+limit].prefetch_related(
            'bedroom_set',
            'bath_set',
            'review_set',
            'roomimage_set',
            'wishlist_set',
            'amenities'
        )

        rooms = []
        for room in room_qs:
            num_beds = 0
            for bedroom in room.bedroom_set.all():
                num_beds_dict = bedroom.bed_set.aggregate(quantity=Sum('quantity'))
                num_beds += num_beds_dict['quantity'] if num_beds_dict['quantity'] else 0
            ratings_dict = room.review_set.aggregate(\
                *[Avg(field) for field in ['rating__cleanliness', 'rating__communication', \
                   'rating__check_in', 'rating__accuracy', 'rating__location', 'rating__value']])
            overall_rating = 0 if None in ratings_dict.values() else sum(ratings_dict.values())/6
            is_wishlist = True if user and room.wishlist_set.filter(user=user).exists() else False
            room_dict = {
                'room_id'        : room.id,
                'title'          : room.title,
                'property_type'  : room.property_type.name,
                'max_capacity'   : room.max_capacity,
                'bedrooms'       : room.bedroom_set.count(),
                'beds'           : num_beds,
                'baths'          : room.bath_set.count(),
                'features'       : list(room.amenities.values_list('name', flat=True)[:3]),
                'rating'         : overall_rating,
                'reviews'        : Review.objects.filter(room=room).count(),
                'price'          : room.price,
                'discount_rate'  : calculate_discounts(room, check_in_date, check_out_date),
                'images'         : list(room.roomimage_set.values_list('image_url', flat=True)),
                'latitude'       : room.latitude, 
                'longitude'      : room.longitude,
                'is_wishlist'    : is_wishlist
            }
            rooms.append(room_dict)
        return JsonResponse({'rooms':rooms, 'total_rooms':len(rooms)}, status=200)

class RoomDetailView(View):
    @check_user_status
    def get(self, request, room_id):
        try:
            user            = request.user
            adults          = int(request.GET.get('adults', 0))
            children        = int(request.GET.get('children', 0))
            infants         = request.GET.get('infants', 0)
            check_in        = request.GET.get('checkin', None)
            check_in_date   = datetime.datetime.strptime(check_in, '%Y-%m-%d') if check_in else None
            check_out       = request.GET.get('checkout', None)
            check_out_date  = datetime.datetime.strptime(check_out, '%Y-%m-%d') if check_out else None
            room            = Room.objects.filter(id=room_id).prefetch_related(
                'review_set',
                'characteristics',
                'shared_spaces',
                'safety_facilities',
                'amenities'
            ).first()
            bedroom_cache   = Bedroom.objects.filter(room=room).prefetch_related('bed_set')
            review_cache    = Review.objects.filter(room=room, reviewer__name='guest').select_related('rating')
            num_beds = 0
            for bedroom in bedroom_cache:
                num_beds += bedroom.bed_set.aggregate(Sum('quantity'))['quantity__sum'] if bedroom.bed_set.aggregate(Sum('quantity'))['quantity__sum'] else 0
            
            bedroom_info = [
                {
                    'room_name'     : bedroom.name,
                    'bed_info'      : [{
                            'size'      : bed.size.name,
                            'quantity'  : bed.quantity,
                        } for bed in bedroom.bed_set.all()
                    ]
                } for bedroom in bedroom_cache
            ]
            bath_info = [
                {
                    'type'      : bath.style,
                    'quantity'  : bath.quantity, 
                } for bath in room.bath_set.all()
            ]
            room_info   = {
                'room_id'           : room.id,
                'host_name'         : room.host.fullname,
                'host_avatar'       : room.host.profile.avatar_image,
                'profile_header'    : room.host.profile.profile_header,
                'title'             : room.title,
                'address'           : room.address,
                'description'       : room.description,
                'rules'             : room.rules,
                'check_in'          : room.check_in.strftime("%-I:%M"),
                'check_out'         : room.check_out.strftime("%-I:%M"),
                'property_type'     : room.property_type.name,
                'place_type'        : room.place_type.name,
                'max_capacity'      : room.max_capacity,
                'bedrooms'          : bedroom_cache.count(),
                'beds'              : num_beds,
                'price'             : room.price,
                'discount_rate'     : calculate_discounts(room, check_in_date, check_out_date),
                'images'            : list(room.roomimage_set.values_list('image_url', flat=True)),
                'latitude'          : room.latitude,
                'longitude'         : room.longitude,
                'blocked_dates'     : list(room.blockeddate_set.values('start_date', 'end_date')),
                'booked_dates'      : list(Booking.objects.filter(room=room, status__name='upcoming').values('start_date', 'end_date')),
                'is_wishlist'       : True if user and Wishlist.objects.filter(room=room, user=user).exists() else False
            }
            characteristics = [
                {
                    'title'         : characteristic.title,
                    'description'   : characteristic.description,
                    'icon_fa'       : characteristic.icon_fa
                } for characteristic in room.characteristics.all()
            ] 
            amenities = [
                {
                    'name'     : amenity.name,
                    'icon_fa'  : amenity.icon_fa
                } for amenity in room.amenities.all()
            ] 
            safety_facilities = [
                {
                    'name'      : facility.name,
                    'icon_fa'   : facility.icon_fa
                } for facility in room.safety_facilities.all()
            ] 
            shared_spaces = [
                {
                    'name'      : space.name,
                    'icon_fa'   : space.icon_fa
                } for space in room.shared_spaces.all()
            ] 
            reviews = [
                {
                    'name'          : review.guest.username,
                    'avatar'        : review.guest.profile.avatar_image,
                    'content'       : review.content,
                    'created_at'    : review.created_at
                } for review in review_cache
            ] 
            ratings_dict = room.review_set.aggregate(\
                *[Avg(field) for field in ['rating__cleanliness', 'rating__communication', 'rating__check_in', \
                    'rating__accuracy', 'rating__location', 'rating__value']])
            for key in ratings_dict.keys():
                if ratings_dict[key] is None:
                    ratings_dict[key] = 0
            overall = sum(ratings_dict.values())/6
            ratings = {
                'cleanliness'   : ratings_dict['rating__cleanliness__avg'],
                'communication' : ratings_dict['rating__communication__avg'],
                'check_in'      : ratings_dict['rating__check_in__avg'],
                'accuracy'      : ratings_dict['rating__accuracy__avg'],
                'location'      : ratings_dict['rating__location__avg'],
                'value'         : ratings_dict['rating__value__avg'],
                'overall'       : overall 
            }

            return JsonResponse({
                'room_info':room_info, 'bedroom_info':bedroom_info, 'bath_info':bath_info,
                'characteristics':characteristics, 'amenities':amenities, 'safety_facilities':safety_facilities,
                'shared_spaces':shared_spaces, 'reviews':reviews, 'ratings':ratings, 'monthly_discount':0.1
            }, status=200)
        except Room.DoesNotExist:
            return JsonResponse({'error':'ROOM_NOT_FOUND'}, status=404)

class RegisterRoomView(View):
    @login_required
    def post(self, request):
        try:
            data              = json.loads(request.body)
            data              = data['inputs']
            bedroom_data      = data['bedroom']
            print(bedroom_data)
            bedroom_data      = bedroom_data[0]
            user              = request.user
            title             = data.get('title')
            address           = data.get('address')
            features          = data.get('features')
            safety_facilities = data.get('safety_facilities' )
            shared_spaces     = data.get('shared_spaces' )
            start_date        = data.get('blockeddate_start')
            start_date        = datetime.datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
            end_date          = data.get('blockeddate_end')
            end_date          = datetime.datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
            check_in          = data.get('check_in')
            check_out         = data.get('check_out')
            if not title or not address or not check_in or not check_out:
                return JsonResponse({'message':'Not Enogh Data'}, status = 400)
            new_room = Room.objects.create(
                    host_id          = request.user.id,
                    title            = data.get('title'),
                    max_capacity     = data.get('max_capacity', 0),
                    address          = data.get('address'),
                    check_in         = check_in,
                    check_out        = check_out,
                    rules            = data.get('rules', " "),
                    description      = data.get('description'," "),
                    price            = data.get("price", 0),
                    place_type_id    = data.get('place_type'),
                    property_type_id = data.get('property_type'),
                    monthly_stay     = data.get('monthly_stay', False),
                    latitude         = 33.49381,
                    longitude        = 127.30484)
            new_bedroom = Bedroom.objects.create(
                room = new_room,
                name = bedroom_data['name']
                )
            Bed.objects.create(
                    bedroom  = new_bedroom,
                    size_id  = bedroom_data['bed'].get('size', 1),
                    quantity = bedroom_data['bed'].get('quantity', 1))
            if features:
                for i in range(len(features)):
                    i -= 1
                    RoomAmenity(
                        room        = new_room,
                        amenity_id  = int(features[i])).save()
            if safety_facilities:
                for i in range(len(safety_facilities)):
                    RoomSafetyFacility(
                        room        = new_room,
                        amenity_id  = int(safety_facilities[i])).save()
            if shared_spaces:
                for i in range(len(safety_facilities)):
                    RoomSharedSpace(
                        room        = new_room,
                        amenity_id  = int(shared_spaces[i])).save()
            Bath(
                room      = new_room,
                style     = data.get('bathroom_type', " "),
                quantity  = int(data.get('bathroom', 0))
                )
            BlockedDate(
                room        = new_room,
                start_date  = start_date,
                end_date    = end_date
                )
            file = request.FILES['filename']
            s3_client = boto3.client(
                    's3',
                    aws_access_key_id     = S3_ACCESS_KEY_ID,
                    aws_secret_access_key = S3_SECRET_ACCESS_KEY
                )
            s3_client.upload_fileobj(
                file,
                "codebnb-s3",
                file.name,
                ExtraArgs={
                    "ContentType": file.content_type})
            image_url       = S3URL+file.name
            image_url       = image_url.replace(" ", "+")
            RoomImage.objects.create(room  = new_room, image_url = image_url)
            return HttpResponse(status = 200)
        except KeyError:
            return JsonResponse({'error':'INVALID_KEY'}, status=400)
