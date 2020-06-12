from django.db import models

class Room(models.Model):
    host              = models.ForeignKey('user.User', on_delete=models.SET_NULL, null=True)
    title             = models.CharField(max_length=50)
    address           = models.CharField(max_length=200)
    description       = models.CharField(max_length=3000, null=True, blank=True)
    rules             = models.TextField(null=True, blank=True)
    price             = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_capacity      = models.IntegerField()
    check_in          = models.TimeField()
    check_out         = models.TimeField()
    latitude          = models.DecimalField(max_digits=9, decimal_places=6)
    longitude         = models.DecimalField(max_digits=9, decimal_places=6)
    monthly_stay      = models.BooleanField(default=False)
    amenities         = models.ManyToManyField('Amenity', through='RoomAmenity')
    safety_facilities = models.ManyToManyField('SafetyFacility', through='RoomSafetyFacility')
    shared_spaces     = models.ManyToManyField('SharedSpace', through='RoomSharedSpace')
    characteristics   = models.ManyToManyField('Characteristic', through='RoomCharacteristic')
    place_type        = models.ForeignKey('PlaceType', on_delete=models.SET_NULL, null=True)
    property_type     = models.ForeignKey('PropertyType', on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return self.title

    class Meta:
        db_table = 'rooms'

class RoomImage(models.Model):
    room        = models.ForeignKey('Room', on_delete=models.SET_NULL, null=True)
    image_url   = models.URLField(null=True)

    class Meta:
        db_table = 'images'

class Characteristic(models.Model):
    title       = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    icon_fa     = models.CharField(max_length=50)

    class Meta:
        db_table = 'characteristics'
        
class Bath(models.Model):
    room        = models.ForeignKey('Room', on_delete=models.SET_NULL, null=True)
    style       = models.CharField(max_length=50)
    quantity    = models.PositiveIntegerField()

    class Meta:
        db_table = 'baths'

class Bedroom(models.Model):
    room = models.ForeignKey('Room', on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=30)
    
    def __str__(self):
        return self.name

    class Meta:
        db_table = 'bedrooms'

class BlockedDate(models.Model):
    room        = models.ForeignKey('Room', on_delete=models.SET_NULL, null=True)
    start_date  = models.DateField()
    end_date    = models.DateField()

    class Meta:
        db_table = 'blocked_dates' 

class SharedSpace(models.Model):
    name    = models.CharField(max_length=50)
    icon_fa = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'shared_spaces'

class SafetyFacility(models.Model):
    name    = models.CharField(max_length=50)
    icon_fa = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'safety_facilities'

class Amenity(models.Model):
    name    = models.CharField(max_length = 50)
    icon_fa = models.CharField(max_length=50)

    def __str__(self):
        return self.name 

    class Meta:
        db_table = 'amenities'

class BedSize(models.Model):
    name = models.CharField(max_length = 50)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'bed_sizes'

class PlaceType(models.Model):
    name = models.CharField(max_length = 50)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'place_types'

class PropertyType(models.Model):
    name = models.CharField(max_length = 50)

    def __str__(self):
        return self.name 

    class Meta:
        db_table = 'property_types'

class RoomSharedSpace(models.Model):
    room            = models.ForeignKey('Room', on_delete = models.CASCADE)
    shared_space    = models.ForeignKey('SharedSpace', on_delete = models.CASCADE)

    class Meta:
        db_table = 'room_shared_spaces'

class RoomSafetyFacility(models.Model):
    room            = models.ForeignKey('Room', on_delete = models.CASCADE)
    safety_facility = models.ForeignKey('SafetyFacility', on_delete = models.CASCADE)

    class Meta:
        db_table = 'room_safety_facilities'

class RoomAmenity(models.Model):
    room    = models.ForeignKey('Room', on_delete = models.CASCADE)
    amenity = models.ForeignKey('Amenity', on_delete = models.CASCADE)

    class Meta:
        db_table = 'room_amenities'

class Bed(models.Model):
    bedroom     = models.ForeignKey('Bedroom', on_delete = models.CASCADE)
    size        = models.ForeignKey('BedSize', on_delete = models.CASCADE)
    quantity    = models.IntegerField()

    class Meta:
        db_table = 'beds'

class RoomCharacteristic(models.Model):
    room            = models.ForeignKey('Room', on_delete=models.CASCADE)
    characteristics = models.ForeignKey('Characteristic', on_delete=models.CASCADE)

    class Meta:
        db_table = 'room_characteristics'
