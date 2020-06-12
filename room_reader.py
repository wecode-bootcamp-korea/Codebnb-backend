import os
import django
import csv
import sys
import json
import datetime
from random import randint

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'codebnb.settings')
django.setup()

from room.models import *
from user.models import *

CSV_PATH_ROOMS = '../stays.csv'

def insert_rooms():
    with open(CSV_PATH_ROOMS) as in_file:
        data_reader = csv.reader(in_file)
        next(data_reader, None)

        for row in data_reader:
            title           = row[0]
            host_username   = row[1]
            address         = row[2]
            description     = row[3]
            capacity        = int(row[4].replace("인원 ", "").replace("명", ""))
            image_urls      = row[5].replace("[", "").replace("]", "").replace("'", "").split(", ")

            profile = UserProfile(
                profile_header           = f"안녕하세요, {host_username}입니다.",
                currency_id              = 1,
                preferred_language_id    = 1
            )
            profile.save()
            user = User(
                username    = host_username,
                fullname    = host_username,
                is_host     = True,
                profile     = profile
            )
            user.save()
            UserLanguage.objects.create(
                user        = user,
                language_id = 1 
            )
            UserLanguage.objects.create(
                user        = user,
                language_id = 2
            )
            check_in_options = {
                '3' : datetime.time(15, 0, 0),
                '4' : datetime.time(16, 0, 0),
                '5' : datetime.time(17, 0, 0),
                '6' : datetime.time(18, 0, 0)
            }
            check_out_options = {
                '11' : datetime.time(11, 0, 0),
                '12' : datetime.time(12, 0, 0),
                '13' : datetime.time(13, 0, 0),
                '14' : datetime.time(14, 0, 0)
            }
            room = Room(
                host            = user,
                title           = title,
                address         = address,
                description     = description,
                max_capacity    = capacity,
                check_in        = check_in_options[str(randint(3, 6))],
                check_out       = check_out_options[str(randint(11, 14))],
                latitude        = 35.1796000,
                longitude       = 129.0756000,
                monthly_stay    = True if randint(1, 2) == 1 else False
            )
            room.save()

            if int(room.max_capacity) >= 6:
                for i in range(1, 4):
                    Bedroom.objects.create(
                        room = room,
                        name = f"{i}번 침실"
                    )
            elif room.max_capacity >= 4:
                for i in range(1, 3):
                    Bedroom.objects.create(
                        room = room,
                        name = f"{i}번 침실"
                    )
            elif room.max_capacity > 2:
                Bedroom.objects.create(
                        room = room,
                        name = "1번 침실"
                )
            else:
                Bedroom.objects.create(
                        room = room,
                        name = "공용 공간"
                )
            
            Bath.objects.create(
                room     = room,
                style    = '단독 사용 욕실',
                quantity = 1
            )

            if len(image_urls) > 1:
                for image in image_urls:
                    RoomImage.objects.create(
                        room      = room,
                        image_url = image
                    )

            repeats = []
            count = 0
            # randomly choose 3 options
            while count < 3:
                i = randint(1, 6)
                if not i in repeats:
                    repeats.append(i)
                    RoomCharacteristic.objects.create(
                        room                = room,
                        characteristics_id  = i  
                    )
                    count += 1

            repeats.clear()
            count = 0
            # randomly choose 3 options
            while count < 3:
                i = randint(1, 8)
                if not i in repeats:
                    repeats.append(i)
                    RoomSharedSpace.objects.create(
                        room                = room,
                        shared_space_id     = i 
                    )
                    count += 1

            repeats.clear()
            count = 0
            # randomly choose 2 options
            while count < 2:
                i = randint(1, 5)
                if not i in repeats:
                    repeats.append(i)
                    RoomSafetyFacility.objects.create(
                        room                = room,
                        safety_facility_id  = i 
                    )
                    count += 1

            repeats.clear()
            count = 0
            # randomly choose 8 options
            while count < 8:
                i = randint(1, 13)
                if not i in repeats:
                    repeats.append(i)
                    RoomAmenity.objects.create(
                        room        = room,
                        amenity_id  = i 
                    )
                    count += 1

insert_rooms()