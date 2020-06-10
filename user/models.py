from django.db import models

from booking.models import Booking
from room.models import Room

class User(models.Model):
    username        = models.CharField(max_length=50)
    fullname        = models.CharField(max_length=50)
    gender          = models.ForeignKey('Gender', on_delete=models.SET_NULL, null=True)
    profile         = models.OneToOneField('UserProfile', on_delete=models.SET_NULL, null=True)
    birthdate       = models.DateField(null=True)
    phone           = models.CharField(max_length=50, null=True)
    address         = models.CharField(max_length=200, null=True)
    emergency_phone = models.CharField(max_length=50, null=True)
    is_host         = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True)
    reviews         = models.ManyToManyField('self', through='Review', symmetrical=False)
    platforms       = models.ManyToManyField('LoginPlatform', through='LoginInfo')
    
    def __str__(self):
        return username
    
    class Meta:
        db_table = 'users'

class UserProfile(models.Model):
    avatar_image        = models.URLField(max_length=2000, null=True)
    profile_header      = models.CharField(max_length=50, null=True)
    profile_message     = models.CharField(max_length=1000, null=True)
    occupation          = models.CharField(max_length=50, null=True)
    residence           = models.CharField(max_length=50, null=True)
    currency            = models.ForeignKey('booking.Currency', on_delete=models.SET_NULL, null=True)
    preferred_language  = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return profile_header
    
    class Meta:
        db_table = 'user_profiles'

class LoginInfo(models.Model):
    email         = models.CharField(max_length=50)
    platform      = models.ForeignKey('LoginPlatform', on_delete=models.CASCADE)
    user          = models.ForeignKey('User', on_delete=models.CASCADE)

    def __str__(self):
        return user.username + "'s login info"

    class Meta:
        db_table = 'login_info'

class LoginPlatform:
    name    = models.CharField(max_length=30)

    def __str__(self):
        return name

    class Meta:
        db_table = 'login_platform

class Wishlist(models.Model):
    user    = models.ForeignKey('User', on_delete=models.CASCADE)
    room    = models.ForeignKey('room.Room', on_delete=models.CASCADE)
    tag     = models.ForeignKey('WishlistTag', on_delete=models.CASCADE)

    def __str__(self):
        return user.username + "'s saved rooms"
    
    class Meta:
        db_table = 'wishlists'

class WishlistTag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return name  
    
    class Meta:
        db_table = 'wishlist_tags'

class Gender(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        db_table = 'genders'

class UserLanguage(models.Model):
    user     = models.ForeignKey('User', on_delete=models.CASCADE)
    language = models.ForeignKey('Language', on_delete=models.CASCADE)

    class Meta:
        db_table = 'user_languages'

class Language(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return name 
    
    class Meta:
        db_table = 'languages'
