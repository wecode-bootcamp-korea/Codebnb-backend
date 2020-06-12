import json
import datetime

from .models import Room, RoomAmenity, RoomCharacteristic, RoomSafetyFacility, RoomSharedSpace
from django.test import TestCase, Client
from unittest.mock import patch, MagicMock

class ListTest(TestCase):
    @classmethod
    def setUp(self):
        room = Room(
            title            = "World's best house for nomad coders",
            address          = "Gangnam-gu, 서울, 대한민국",
            description      = "5G internet, complimentary thunderbolt cables, 3 minutes walk to Seonleung station,\
                house equipment include iMac, 16-inch MacBook pro, and Keychron wireless mechanical keyboard.",
            price            = 130.00,
            max_capacity     = 4,
            check_in         = datetime.time(15-00-00),
            check_out        = datetime.time(12-00-00),
            latitude         = 37.501670,
            longitude        = 127.035530,
            monthly_stay     = True,
            place_type_id    = 1,
            property_type_id = 2  
        )
        room.save()
        # for i in range(1, 4):
        #     RoomAmenity.objects.create(
        #         room         = room,
        #         amenity_id   = i   
        #     )
        # for i in range(1, 3):
        #     RoomSharedSpace.objects.create(
        #         room            = room,
        #         shared_space_id = i
        #     )
        # for i in range(1, 3):
        #     RoomSafetyFacility.objects.create(
        #         room               = room,
        #         safety_facility_id = i 
        #     )
        # for i in range(1, 3):
        #     RoomCharacteristic.objects.create(
        #         room               = room,
        #         characteristics_id = i 
        #     )

    def tearDown(self):
        Room.objects.all().delete()
        RoomAmenity.objects.all().delete()
        RoomSharedSpace.objects.all().delete()
        RoomSafetyFacility.objects.all().delete()
        RoomCharacteristic.objects.all().delete()

    def test_roomlistview_get_success(self):
        client = Client()
        response = client.get('/room/list?location=서울')

        self.assertEqual(response.json(),
            {
                "rooms": [{
                    "room_id"       : 8,
                    "title"         : "[10sec to Gangnam sta.] New! Great View & Clean!",
                    "property_type" : "아파트",
                    "max_capacity"  : 2,
                    "bedrooms"      : 0,
                    "beds"          : 0,
                    "baths"         : 1,
                    # "features"      : [
                    #     "옷장 / 서랍장",
                    #     "업무 가능 공간 / 책상",
                    #     "에어컨"
                    # ],
                    "rating"        : 0.0,
                    "reviews"       : 0,
                    "price"         : "130.00",
                    "discount_rate" : 0.1,
                    "images"        : [],
                    "latitude"      : "37.501670",
                    "longitude"     : "127.035530",
                    "is_wishlist"   : false
                }],
                "total_rooms" : 1
            }
        )
        self.assertEqual(response.status_code, 200)
    
    def test_roomlistview_get_not_found(self):
        client = Client()
        response = client.get('/room/lists?location=서울')
        self.assertEqual(response.status_code, 404)

class DetailTest(TestCase):
    def setUp(self):
        room = Room(
            title            = "World's best house for nomad coders",
            address          = "Gangnam-gu, 서울, 대한민국",
            description      = "5G internet, complimentary thunderbolt cables, 3 minutes walk to Seonleung station,\
                house equipment include iMac, 16-inch MacBook pro, and Keychron wireless mechanical keyboard.",
            price            = 130.00,
            max_capacity     = 4,
            check_in         = datetime.time(15-00-00),
            check_out        = datetime.time(12-00-00),
            latitude         = 37.501670,
            longitude        = 127.035530,
            monthly_stay     = True,
            place_type       = PlaceType.objects.create(),
            property_type_id = 2  
        )
        room.save()
        # for i in range(1, 4):
        #     RoomAmenity.objects.create(
        #         room         = room,
        #         amenity_id   = i   
        #     )
        # for i in range(1, 3):
        #     RoomSharedSpace.objects.create(
        #         room            = room,
        #         shared_space_id = i
        #     )
        # for i in range(1, 3):
        #     RoomSafetyFacility.objects.create(
        #         room               = room,
        #         safety_facility_id = i 
        #     )
        # for i in range(1, 3):
        #     RoomCharacteristic.objects.create(
        #         room               = room,
        #         characteristics_id = i 
        #     )
        # bedroom = Bedroom(room=room, name='1번 침실')
        # bedroom.save()
        # Bed.objects.create(bed_size_id=1, quantity=1, bedroom=bedroom)
        # Bath.objects.create(room=room, style='공용', quantity=1)

    def tearDown(self):
        Room.objects.delete()
        RoomAmenity.objects.all().delete()
        RoomSharedSpace.objects.all().delete()
        RoomSafetyFacility.objects.all().delete()
        RoomCharacteristic.objects.all().delete()
        Bedroom.objects.all().delete()
        Bath.objects.all().delete()
        Bed.objects.all().delete()
    
    def test_roomdetailview_get_success(self):
        client = Client()
        response = client.get('/room/detail/1')
        self.assertEqual(response.json(),
            {
                "room_info" : {
                    "host_name"     : null,
                    "host_avatar"   : null,
                    "title"         : "도민들에게도 인정받은 애월의 절경을 볼수있는숙소 해밀공간",
                    "address"       : "Aewol-eup, Jeju-si, 제주도, 한국",
                    "description"   : "안녕하세요~ 저는 어머니랑 해밀공간을 운영중인 맥스입니다! 저희 공간의 자리는 옛날시대의 우리나라 병사들이 왜적의 침입을 감시하던 초소 였습니다. 그래서인지 해밀에서는 제주시를 180'각도로 한눈에 담을수 있는 전망을 보실수있어요^^  앞쪽으로는 도시에서는 상상할수없는 전망 뒤쪽으로는 한라산이 보이는 저희 해밀공간으로 오세요~   ☎️ 064 - 799 -3033 ☎️ 언제든지 전화, 문자, 카톡 문의 가능합니다.????  숙소 더블싱글 베드가 구비되어있어요~  게스트 이용 가능 공간/시설 #해밀 (객실)  #비갠가든 (야외 바비큐장)  #비온 뒤 맑게 갠 하늘 (CAFE)",
                    "rules"         : "기타 주의사항\r\n객실 내 흡연, 취사는 금지입니다.\r\n애완동물은 입실이 불가합니다.\r\n다른객실의 손님들을 위해서 심야에는 고성방가, 음주가무는 삼가주시기 바랍니다.",
                    "check_in"      : "15:00:00",
                    "check_out"     : "12:00:00",
                    "property_type" : "아파트",
                    "place_type"    : "집전체",
                    "max_capacity"  : 4,
                    "bedrooms"      : 1,
                    "beds"          : 1,
                    "price"         : "130.00",
                    "discount_rate" : 0.1,
                    "images"        : [],
                    "latitude"      : "37.501670",
                    "longitude"     : "127.035530",
                    "blocked_dates" : [],
                    "booked_dates"  : [],
                    "is_wishlist"   : false
                },
                "bedroom_info": [
                    # {
                    #     "room_name": "1번 침실",
                    #     "bed_info": [
                    #         {
                    #             "size": "킹사이즈",
                    #             "quantity": 1
                    #         }
                    #     ]
                    # },
                ],
                "bath_info": [
                    # {
                    #     "type": "공용",
                    #     "quantity": 1
                    # }
                ],
                "characteristics": [
                    # {
                    #     "title": "엘리베이터",
                    #     "description": "해당 지역에서 이 편의시설을 갖추고 있는 보기 드문 숙소입니다."
                    # },
                    # {
                    #     "title": "순조로운 체크인 과정",
                    #     "description": "최근 숙박한 게스트 체크인 과정을 칭찬한 숙소입니다."
                    # },
                ],
                "amenities": [],
                "safety_facilities": [
                    # "화재감지기",
                    # "일산화탄소 감지기"
                ],
                "shared_spaces": [
                    # "거실",
                    # "주방"
                ],
                "reviews": [],
                "ratings": {
                    "cleanliness": null,
                    "communication": null,
                    "check_in": null,
                    "accuracy": null,
                    "location": null,
                    "value": null,
                    "overall": null
                },
                "monthly_discount": 0.1
            }
        )
        self.assertEqual(response.status_code, 200)

    def test_roomdetailview_get_fail(self):
        client = Client()
        response = client.get('/room/detail/132')
        self.assertEqual(response.json(),
            {
                "error": "INVALID_ROOM_ID"
            }
        )
        self.assertEqual(response.status_code, 400)
    
    def test_roomdetailview_get_not_found(self):
        client = Client()
        response = client.get('room/details/2')
        self.assertEqual(response.status_code, 404)