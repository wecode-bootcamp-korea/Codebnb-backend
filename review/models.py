from django.db import models

from user.models import User 
from room.models import Room

class Review(models.Model):
    room       = models.ForeignKey('room.Room', on_delete=models.SET_NULL, null=True)
    reviewer   = models.ForeignKey('ReviewerType', on_delete=models.SET_NULL, null=True)
    host       = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='host_reviews')
    guest      = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='guest_reviews')
    rating     = models.OneToOneField('Rating', on_delete=models.SET_NULL, null=True)
    content    = models.CharField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return content[:20]
    
    class Meta:
        db_table = 'reviews'

class ReviewerType(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        db_table = 'reviewer_types'

class Rating(models.Model):
    cleanliness     = models.PositiveIntegerField()
    communication   = models.PositiveIntegerField()
    check_in        = models.PositiveIntegerField()
    accuracy        = models.PositiveIntegerField()
    location        = models.PositiveIntegerField()
    value           = models.PositiveIntegerField()

    class Meta:
        db_table = 'ratings'
